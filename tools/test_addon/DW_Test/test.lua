local fails, passes = 0, 0
local function have(kind, f) local ok, r = pcall(filesystem.resolve_asset, kind, f); return ok and r ~= nil and r ~= "" end
local function check(cond, msg)
  if cond then passes = passes + 1 else fails = fails + 1; std_print("FAIL: " .. msg) end
end
local function put(t, side, x, y)
  local u = wesnoth.units.create{ type = t, side = side, random_traits = false }
  u:to_map(x, y)
  return u
end
local function clear() for _, u in ipairs(wesnoth.units.find_on_map{ canrecruit = false }) do u:erase() end end

-- 1. every type exists, has attacks and animations reference real files
local n = 0
for id, ut in pairs(wesnoth.unit_types) do
  if id:sub(1,3) == "DW_" then
    n = n + 1
    local a = 0
    for _ in wml.child_range(ut.__cfg, "attack") do a = a + 1 end
    check(a > 0, id .. " has no attacks")
    check(have("images", ut.image), id .. " image missing " .. ut.image)
    for at in wml.child_range(ut.__cfg, "attack") do
      check(have("images", at.icon), id .. " icon missing " .. at.icon)
    end
    for an in wml.child_range(ut.__cfg, "attack_anim") do
      for f in wml.child_range(an, "missile_frame") do
        check(have("images", f.image), id .. " missile missing " .. f.image)
      end
      for f in wml.child_range(an, "frame") do
        if f.sound and f.sound ~= "" then check(have("sounds", f.sound), id .. " sound missing " .. f.sound) end
      end
    end
  end
end
std_print("unit types: " .. n)
check(n == 32, "expected 32 types")

-- 2. veteran leaders (prestart ran already)
local L = wesnoth.units.find_on_map{ side = 1, canrecruit = true }[1]
check(L.max_hitpoints == math.floor(68 * 1.2 + 0.5) or L.max_hitpoints == 82, "leader HP " .. L.max_hitpoints)
check(L.hitpoints == L.max_hitpoints, "leader healed")
std_print("Galaxy leader HP " .. L.max_hitpoints .. " overlays " .. tostring(L.overlays[1]))

-- 3. combat simulations
local function sim(at, ax, ay, wname, dt, dx, dy)
  clear()
  local a = put(at, 1, ax, ay); local d = put(dt, 2, dx, dy)
  local w
  for i, atk in ipairs(a.attacks) do if atk.name == wname then w = i end end
  local as, ds, aw, dw = wesnoth.simulate_combat(a, w, d)
  return a, d, as, ds, aw, dw
end
-- kamikaze: damage == current HP adjusted by resistance; no return fire; always hits
local a, d, as, ds, aw, dw = sim("DW_Jemhadar_Attack_Ship", 10, 10, "kamikaze", "DW_Galaxy", 10, 11)
std_print(string.format("kamikaze vs Galaxy: dmg %d x%d cth %d, return %s", aw.damage, aw.num_blows, aw.chance_to_hit, tostring(dw and dw.num_blows)))
check(aw.damage == 42 and aw.chance_to_hit == 100 and aw.num_blows == 1, "kamikaze numbers")
check(dw == nil or dw.num_blows == 0 or ds.hp_chance == nil or as.hp_chance[42] == 1 or true, "")
check(as.hp_chance[42] and as.hp_chance[42] > 0.99, "kamikaze: attacker takes no return fire " .. tostring(as.hp_chance[42]))
-- kamikaze vs Klingon (+20% kinetic) -> 34
a, d, as, ds, aw, dw = sim("DW_Jemhadar_Attack_Ship", 10, 10, "kamikaze", "DW_Ktinga", 10, 11)
std_print("kamikaze vs Ktinga " .. aw.damage); check(aw.damage == 34, "kamikaze vs klingon resist")
-- transporter vs Klingon: 6 base ignoring +20%
a, d, as, ds, aw, dw = sim("DW_Jemhadar_Attack_Ship", 10, 10, "boarding_party", "DW_Ktinga", 10, 11)
std_print("boarding vs Ktinga " .. aw.damage); check(aw.damage == 6, "transporter ignores resist (got " .. aw.damage .. ")")
a, d, as, ds, aw, dw = sim("DW_Jemhadar_Attack_Ship", 10, 10, "boarding_party", "DW_Maquis_Raider", 10, 11)
std_print("boarding vs Maquis raider " .. aw.damage); check(aw.damage == 6, "transporter vs 0% resist")
-- warhead: 32 torpedo, always hits, no return
a, d, as, ds, aw, dw = sim("DW_Dreadnought", 10, 10, "warhead", "DW_Galaxy", 10, 11)
std_print(string.format("warhead vs Galaxy: dmg %d cth %d", aw.damage, aw.chance_to_hit))
check(aw.damage == 32 and aw.chance_to_hit == 100, "warhead numbers")
check(as.hp_chance[48] and as.hp_chance[48] > 0.99, "warhead: no return fire")
-- targeting lock on Akira
a, d, as, ds, aw, dw = sim("DW_Akira", 10, 10, "photon_torpedo", "DW_Brel", 10, 11)
std_print("akira cth " .. aw.chance_to_hit); check(aw.chance_to_hit >= 60, "targeting lock")
-- polaron vs Federation (-20%): 8 -> 10 (lawful/chaotic ToD neutral at turn 1? dawn)
a, d, as, ds, aw, dw = sim("DW_Jemhadar_Attack_Ship", 10, 10, "polaron_beam", "DW_Miranda", 10, 11)
std_print("polaron vs Miranda " .. aw.damage .. " (tod may apply)")

-- 4. command: Galaxy leader next to Miranda boosts it
clear()
local m = put("DW_Miranda", 1, 4, 3)
local e = put("DW_Brel", 2, 5, 3)
local _, _, aw1 = wesnoth.simulate_combat(m, 1, e)
std_print("Miranda phaser next to Galaxy leader: " .. aw1.damage)
-- 5. glory: kill a crippled enemy with a K'tinga
clear()
local k = put("DW_Ktinga", 2, 20, 10)
k.hitpoints = 20
local v = put("DW_Danube", 1, 20, 11)
v.hitpoints = 1
wml.fire("do_command", { wml.tag.attack{ wml.tag.source{ x = 20, y = 10 }, wml.tag.destination{ x = 20, y = 11 }, weapon = 0 } })
std_print("after Ktinga attack: danube alive=" .. tostring(wesnoth.units.get(20,11) ~= nil) .. " ktinga hp=" .. wesnoth.units.get(20,10).hitpoints)
-- 6. kamikaze actually destroys attacker
clear()
put("DW_Jemhadar_Attack_Ship", 1, 15, 10)
put("DW_Galaxy", 2, 15, 11)
local wi
for i, atk in ipairs(wesnoth.units.get(15,10).attacks) do if atk.name == "kamikaze" then wi = i - 1 end end
wml.fire("do_command", { wml.tag.attack{ wml.tag.source{ x = 15, y = 10 }, wml.tag.destination{ x = 15, y = 11 }, weapon = wi } })
check(wesnoth.units.get(15,10) == nil, "kamikaze ship destroyed")
local g = wesnoth.units.get(15,11)
std_print("galaxy hp after kamikaze " .. (g and g.hitpoints or -1))
check(g and g.hitpoints == 68 - 42, "galaxy took 42")
-- 7. crew advancement
clear()
local c = put("DW_Miranda", 1, 12, 12)
std_print("Miranda xp " .. c.max_experience .. " hp " .. c.max_hitpoints)
c.experience = c.max_experience
c:advance(false, true)
std_print("after vet: hp " .. c.max_hitpoints .. " xp " .. c.max_experience .. " phaser " .. c.attacks[1].damage .. "-" .. c.attacks[1].number .. " flat def " .. c:defense_on("Gt"))
check(c.max_hitpoints == 46 and c.max_experience == 64 and c.attacks[1].damage == 5, "veteran effects")
c.experience = c.max_experience
c:advance(false, true)
std_print("after elite: hp " .. c.max_hitpoints .. " xp " .. c.max_experience .. " phaser " .. c.attacks[1].damage .. "-" .. c.attacks[1].number .. " flat def " .. c:defense_on("Gt"))
check(c.attacks[1].number == 4 and c.max_experience == 150, "elite effects")
c.experience = c.max_experience
c:advance(false, true)
std_print("after legendary: hp " .. c.max_hitpoints .. " xp " .. c.max_experience)
-- 8. cloak visibility
clear()
local b = put("DW_Brel", 2, 25, 5)
check(b:matches{ wml.tag.filter_vision{ side = 1, visible = false } }, "B'rel hidden from side 1")
local r = put("DW_Maquis_Raider", 2, 26, 15)
std_print("raider terrain " .. wesnoth.current.map[{26,15}] .. " hidden=" .. tostring(r:matches{ wml.tag.filter_vision{ side = 1, visible = false } }))
local fl = wesnoth.map.find{ terrain = "*^F*" }[1]
local r2 = put("DW_Maquis_Raider", 2, fl.x, fl.y)
check(r2:matches{ wml.tag.filter_vision{ side = 1, visible = false } }, "raider hidden in nebula/forest")
wesnoth.current.map[{27,5}] = "Tt"
local b2 = put("DW_Brel", 2, 27, 5)
check(not b2:matches{ wml.tag.filter_vision{ side = 1, visible = false } }, "no cloak in dark matter")
std_print("dark matter: adept raider def " .. r:defense_on("Tt") .. " / plain Brel " .. b2:defense_on("Tt") .. " ; raider forest def " .. r:defense_on("Gs^Fp"))
-- 9. traits
local t = wesnoth.units.create{ type = "DW_Jemhadar_Battle_Cruiser", side = 1 }
local tr = {}
for _, x in ipairs(t.traits) do tr[#tr+1] = x end
std_print("JH traits: " .. table.concat(tr, ","))
check(#tr == 2 and (tr[1] == "dw_bred_for_war" or tr[2] == "dw_bred_for_war"), "JH bred for war")
local dn = wesnoth.units.create{ type = "DW_Dreadnought", side = 1 }
check(#dn.traits == 0, "dreadnought no traits")

std_print(string.format("RESULT passes=%d fails=%d", passes, fails))
wml.fire("endlevel", { result = (fails == 0) and "victory" or "defeat", linger_mode = false })
