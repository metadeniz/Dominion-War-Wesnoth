-- The Dominion War: turns a standard Wesnoth map into space terrain when a game starts.
--
-- Runs from the prestart event in {DW_SPACE_TERRAIN_EVENT} (terrain/_main.cfg). Every space
-- terrain is an alias of the Wesnoth terrain it replaces, so movement, defence, villages and
-- castles all play exactly as on the original map. Only the look changes.
--
-- Keep this file and terrain/tools/convert_map.py in step: they hold the same table and rules.
-- Design and mapping: design/space-tileset.md.

local function neighbours(x, y)
	-- 1-based map coordinates: even columns sit half a hex lower
	if x % 2 == 0 then
		return { {x, y - 1}, {x + 1, y}, {x + 1, y + 1}, {x, y + 1}, {x - 1, y + 1}, {x - 1, y} }
	end
	return { {x, y - 1}, {x + 1, y - 1}, {x + 1, y}, {x, y + 1}, {x - 1, y}, {x - 1, y - 1} }
end

local function starts(s, p) return s:sub(1, #p) == p end

local function bridge_dir(o)
	for _, c in ipairs({ "|", "/", "\\" }) do
		if o:find(c, 1, true) then return c end
	end
	return "|"
end

local SNOW_FOREST = { Fpa = true, Fda = true, Fma = true }

-- the new overlay ("" drops it), or "IMP" / "UNWALK" when the overlay makes the hex a barrier
local function convert_overlay(o)
	if o == "" then return "" end
	local o2 = o:sub(1, 2)
	if starts(o, "Xm") or o == "Xo" or ((o2 == "Pr" or o2 == "Pw") and o:sub(-1) ~= "o") then return "IMP" end
	if o == "Qov" or o == "Eqf" then return "UNWALK" end
	local c = o:sub(1, 1)
	if c == "F" then return SNOW_FOREST[o] and "Zfa" or "Zf" end
	if o == "Tf" or o == "Tfi" then return "Zt" end
	if o == "Uf" or o == "Ufi" then return "Zto" end
	if c == "V" then return (o == "Vm" or o == "Vov") and "Zvo" or "Zv" end
	if c == "B" then
		local d = bridge_dir(o)
		if starts(o, "Bs") and not starts(o, "Bsb") then return "Zw" .. d end
		if starts(o, "Br") then return "Zy" .. d end
		return "Zu" .. d
	end
	if o == "Dr" then return "Zr" end
	if o == "Do" then return "Zo" end
	if o == "Cov" then return "Zco" end
	if o == "Kov" then return "Zko" end
	return ""   -- flowers, stones, farms, lights and other decorations: open space
end

local CASTLE_GROUP = { Cea = "a", Coa = "a", Cha = "a", Kea = "a", Koa = "a", Kha = "a",
	Chw = "w", Khw = "w", Chs = "s", Khs = "s", Cm = "r", Cme = "r", Km = "r", Kme = "r" }

-- plain bases; castles, keeps and impassable hexes are settled later from their neighbours
local function convert_base(b)
	local c = b:sub(1, 1)
	if c == "C" or c == "K" then return "CASTLE" end
	if c == "X" then return "IMP" end
	if c == "W" then
		if b == "Wwf" then return "Zsf" end
		if starts(b, "Wo") then return "Zbd" end
		if starts(b, "Wwr") then return "Zbr" end
		return "Zb"
	end
	if c == "S" then return "Zbs" end
	if c == "R" then return starts(b, "Rr") and "Zsl" or "Zs" end
	if c == "U" then
		if starts(b, "Uh") then return "Zvh" end
		if starts(b, "Uu") then return "Zv" end
		return "Zs"
	end
	if c == "T" then return "Zt" end
	if c == "A" then return "Za" end
	if c == "D" then return "Zd" end
	if c == "H" then return (b == "Hd" and "Zhd") or (b == "Ha" and "Zha") or "Zh" end
	if c == "M" then
		if b == "Mv" then return "Zl" end
		return b == "Ms" and "Zma" or "Zm"
	end
	if c == "Q" then return starts(b, "Ql") and "Zl" or "Zq" end
	return "Zs"   -- grass, dirt, floors and anything unknown: open space
end

local function key(x, y) return x * 10000 + y end

-- Impassable hexes are drawn by the shape of their cluster (D, 16 Nov): touching the map's edge,
-- the Void; a lone hex, a black hole, pulsar or eddy; a thick blob, a plasma storm (12+ hexes) or,
-- alternating, the Briar Patch and a radiation zone; a thin line, a chain of gravitational eddies.
local function classify_impassable(imp, list, W, H)
	local out, seen = {}, {}
	local LONE = { "Zxk", "Zxj", "Zxk", "Zxe" }
	local lone_i, area_i = 0, 0
	table.sort(list, function(a, b) return a[1] < b[1] or (a[1] == b[1] and a[2] < b[2]) end)
	for _, p in ipairs(list) do
		if not seen[key(p[1], p[2])] then
			local comp, st = {}, { p }
			seen[key(p[1], p[2])] = true
			while #st > 0 do
				local q = table.remove(st)
				comp[#comp + 1] = q
				for _, n in ipairs(neighbours(q[1], q[2])) do
					local k = key(n[1], n[2])
					if imp[k] and not seen[k] then seen[k] = true; st[#st + 1] = n end
				end
			end
			local edge, thick = false, 0
			for _, q in ipairs(comp) do
				if q[1] <= 1 or q[2] <= 1 or q[1] >= W or q[2] >= H then edge = true end
				local cnt = 0
				for _, n in ipairs(neighbours(q[1], q[2])) do if imp[key(n[1], n[2])] then cnt = cnt + 1 end end
				if cnt >= 4 then thick = thick + 1 end
			end
			local code
			if edge then code = "Zxn"
			elseif #comp == 1 then code = LONE[lone_i % #LONE + 1]; lone_i = lone_i + 1
			elseif thick >= 3 or (thick >= 1 and #comp >= 6) then
				if #comp >= 12 then code = "Zxp"
				else code = (area_i % 2 == 0) and "Zxq" or "Zxr"; area_i = area_i + 1 end
			else code = "Zxe" end
			for _, q in ipairs(comp) do out[key(q[1], q[2])] = code end
		end
	end
	return out
end

return function()
	local map = wesnoth.current.map
	local W, H = map.playable_width, map.playable_height
	local cells, imp, implist, castles = {}, {}, {}, {}
	for y = 0, H + 1 do
		for x = 0, W + 1 do
			local t = map[{x, y}]
			local b, o = t:match("^([^%^]*)%^?(.*)$")
			local k = key(x, y)
			if starts(b, "_") or starts(o, "_") or starts(b, "Z") then
				cells[k] = false              -- off-map, fog and shroud markers, and space already: unchanged
			else
				local nb, no = convert_base(b), convert_overlay(o)
				if nb == "IMP" or no == "IMP" then
					imp[k] = true; implist[#implist + 1] = {x, y}; cells[k] = { x = x, y = y }
				else
					if no == "UNWALK" then nb, no = "Zq", "" end
					if nb == "CASTLE" then
						castles[k] = { x = x, y = y, b = b, o = no }; cells[k] = { x = x, y = y }
					else
						cells[k] = { x = x, y = y, code = nb .. (no ~= "" and ("^" .. no) or "") }
					end
				end
			end
		end
	end
	-- castles: drydocks when joined to a keep, outposts when not (D)
	local joined = {}
	for k, c in pairs(castles) do
		if c.b:sub(1, 1) == "K" and not joined[k] then
			local st = { c }; joined[k] = true
			while #st > 0 do
				local q = table.remove(st)
				for _, n in ipairs(neighbours(q.x, q.y)) do
					local nk = key(n[1], n[2])
					if castles[nk] and not joined[nk] then joined[nk] = true; st[#st + 1] = castles[nk] end
				end
			end
		end
	end
	for k, c in pairs(castles) do
		local g = CASTLE_GROUP[c.b] or ""
		local ruined = c.b:sub(2):find("r", 1, true) ~= nil
		local code
		if c.b:sub(1, 1) == "K" then code = "Zk" .. (ruined and "x" or "") .. g
		elseif joined[k] then code = "Zc" .. (ruined and "b" or "d") .. g
		else code = "Zc" .. (ruined and "x" or "o") .. g end
		cells[k].code = code .. (c.o ~= "" and ("^" .. c.o) or "")
	end
	for k, code in pairs(classify_impassable(imp, implist, W, H)) do cells[k].code = code end
	for _, c in pairs(cells) do
		if c and c.code then map[{c.x, c.y}] = c.code end
	end
end
