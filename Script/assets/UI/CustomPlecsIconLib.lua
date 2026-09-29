
--?-------------------------------------------------------------------------------------------------------------------------------------------------------------
--?                         ____  _     _____ ____ ____     ____ _   _ ____ _____ ___  __  __   ___ ____ ___  _   _ ____
--?                        |  _ \| |   | ____/ ___/ ___|   / ___| | | / ___|_   _/ _ \|  \/  | |_ _/ ___/ _ \| \ | / ___|
--?                        | |_) | |   |  _|| |   \___ \  | |   | | | \___ \ | || | | | |\/| |  | | |  | | | |  \| \___ \
--?                        |  __/| |___| |__| |___ ___) | | |___| |_| |___) || || |_| | |  | |  | | |__| |_| | |\  |___) |
--?                        |_|   |_____|_____\____|____/   \____|\___/|____/ |_| \___/|_|  |_| |___\____\___/|_| \_|____/
--?
--?-------------------------------------------------------------------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------------------------------------------------------------------
--* This is a collection of functions that can be used to draw custom icons in PLECS.
--* The functions are called when PLECS is first started and when a mask icon is updated.

--!--> Please make a copy of this file and place it in the PLECS installation directory under the 'lua' folder.
--!--> Please don't delete or make changes to this file.

----------------------------------------------------------------------------------------------------------------------------------------------------------------
local list = {}

--?-------------------------------------------------------------------------------------------------------------------------------------------------------------
--? HELPER FUNCTIONS
--?-------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Rotate n times by 90 degrees in clockwise direction around the origin. An error is generated if n is not an integer.
-- The clockwise direction was chosen as this is the standard behavior when using the PLECS editor.
local function rotate(x, y, n)
	if n == 0 then
		return x, y
	elseif n == 1 then
		-- clockwise rotation
		x,y = y,x
		for k in ipairs(x) do x[k] = x[k] * -1 end
		return x, y
	elseif n == 2 then
		-- point reflection
		for k in ipairs(x) do x[k] = x[k] * -1 end
		for k in ipairs(y) do y[k] = y[k] * -1 end
		return x, y
	elseif n == 3 then
		-- counter clockwise rotation
		x,y = y,x
		for k in ipairs(y) do y[k] = y[k] * -1 end
		return x, y
	end
	error("The 'rotate' parameter must be an integer multiple of 90.")
	return x, y
end

-- Scale by the provided factor.
local function scale(x, y, scaleX, scaleY)
	if scaleX ~= 1 then
		for k in ipairs(x) do x[k] = x[k] * scaleX end
	end
	if scaleY ~= 1 then
		for k in ipairs(y) do y[k] = y[k] * scaleY end
	end
	return x, y
end

-- Translate by (x0, y0).
local function translate(x, y, x0, y0)
	if x0 ~= 0 then
		for k in ipairs(x) do x[k] = x[k] + x0 end
	end
	if y0 ~= 0 then
		for k in ipairs(y) do y[k] = y[k] + y0 end
	end
	return x, y
end

-- Full coordinate transform. It is assumed that params has been validated before
local function transform(x, y, params)
	local scaleX = params.scale or 1
	local scaleY = params.scale or 1
	if params.flip then scaleY = scaleY * -1 end
	-- We always flip around the x axis before rotating. This is equivalent to flipping the icon about a rotating axis.
	x, y = scale(x, y, scaleX, scaleY)
	x, y = rotate(x, y, params.rotate / 90)
	x, y = translate(x, y, params.x0, params.y0)
	return x, y
end

-- Validates the type of all parameters and throws an error for unknown parameters. Mandatory fields are populated with default values (x0, y0, rotate, flip, wireLength).
-- The returned params table contains valid (copied) entries for all fields.
local function validateInput(x0, y0, params, nTerminals, supportedParams)
	if params == nil then params={} end
	assert(type(params) == "table", "Invalid data type for 'params'. A table ('{}') was expected!")

	local validatedParams = {}

	validatedParams.x0 = x0 or 0
	validatedParams.y0 = y0 or 0
	assert(type(validatedParams.x0) == "number", "Invalid data type for 'x0'. A number was expected!")
	assert(type(validatedParams.y0) == "number", "Invalid data type for 'y0'. A number was expected!")

	validatedParams.scale = params.scale or 1
	assert(type(validatedParams.scale) == "number", "Invalid data type for 'scale'. A number was expected!")

	validatedParams.flip = params.flip or false
	validatedParams.rotate = params.rotate or 0
	assert(type(validatedParams.flip) == "boolean", "Invalid data type for 'flip'. A boolean was expected!")
	assert(type(validatedParams.rotate) == "number", "Invalid data type for 'rotate'. A number was expected!")

	-- Restrict the rotate argument to the range [0, 360)
	validatedParams.rotate = math.fmod(math.fmod(validatedParams.rotate, 360) + 360, 360)

	-- Parse the wireLength parameter
	local wireLength = params.wireLength or 0
	assert(type(wireLength) == "number" or type(wireLength) == "table", "Invalid data type for 'wireLength'. Either a number or a table of numbers was expected!")
	if type(wireLength) == "number" then
		validatedParams.wireLength = {}
		for i = 1, nTerminals do
			validatedParams.wireLength[i] = wireLength
		end
	elseif type(wireLength) == "table" then
		assert((#wireLength == nTerminals), "Invalid number of arguments passed as 'wireLength'.")
		validatedParams.wireLength = {}
		for i = 1, nTerminals do
			validatedParams.wireLength[i] = wireLength[i]
		end
	end

	-- Check additional parameters

	-- shiftGate
	if params.shiftGate ~= nil and supportedParams.shiftGate then
		assert(type(params.shiftGate) == "boolean", "Invalid data type for 'shiftGate'. A boolean was expected!")
		validatedParams.shiftGate = params.shiftGate
	end
	-- deviceType
	if params.deviceType ~= nil and supportedParams.deviceType then
		assert(type(params.deviceType) == "string", "Invalid data type for 'deviceType'. A string was expected!")
		validatedParams.deviceType = params.deviceType
	end
	--showPolarity
	if params.showPolarity ~= nil and supportedParams.showPolarity then
		assert(type(params.showPolarity) == "boolean", "Invalid data type for 'showPolarity'. A boolean was expected!")
		validatedParams.showPolarity = params.showPolarity
	end
	--showArrow
	if params.showArrow ~= nil and supportedParams.showArrow then
		assert(type(params.showArrow) == "boolean", "Invalid data type for 'showArrow'. A boolean was expected!")
		validatedParams.showArrow = params.showArrow
	end
	-- variable
	if params.variable ~= nil and supportedParams.variable then
		assert(type(params.variable) == "boolean", "Invalid data type for 'variable'. A boolean was expected!")
		validatedParams.variable = params.variable
	end
	-- showCore
	if params.showCore ~= nil and supportedParams.showCore then
		assert(type(params.showCore) == "boolean", "Invalid data type for 'showCore'. A boolean was expected!")
		validatedParams.showCore = params.showCore
	end
	-- polarity
	if params.polarity ~= nil and supportedParams.polarity then
		assert(type(params.polarity) == "string", "Invalid data type for 'polarity'. A string was expected!")
		validatedParams.polarity = params.polarity
	end
	-- switchClosed
	if params.switchClosed ~= nil and supportedParams.switchClosed then
		assert(type(params.switchClosed) == "number", "Invalid data type for 'switchClosed'. A number was expected!")
		validatedParams.switchClosed = params.switchClosed
	end
	-- variableResistor
	if params.variableResistor ~= nil and supportedParams.variableResistor then
		assert(type(params.variableResistor) == "boolean", "Invalid data type for 'variableResistor'. A boolean was expected!")
		validatedParams.variableResistor = params.variableResistor
	end
	-- variableInductor
	if params.variableInductor ~= nil and supportedParams.variableInductor then
		assert(type(params.variableInductor) == "boolean", "Invalid data type for 'variableInductor'. A boolean was expected!")
		validatedParams.variableInductor = params.variableInductor
	end
	-- variableCapacitor
	if params.variableCapacitor ~= nil and supportedParams.variableCapacitor then
		assert(type(params.variableCapacitor) == "boolean", "Invalid data type for 'variableCapacitor'. A boolean was expected!")
		validatedParams.variableCapacitor = params.variableCapacitor
	end
	-- flipArrow
	if params.flipArrow ~= nil and supportedParams.flipArrow then
		assert(type(params.flipArrow) == "boolean", "Invalid data type for 'flipArrow'. A boolean was expected!")
		validatedParams.flipArrow = params.flipArrow
	end
	-- showLightning
	if params.showLightning ~= nil and supportedParams.showLightning then
		assert(type(params.showLightning) == "boolean", "Invalid data type for 'showLightning'. A boolean was expected!")
		validatedParams.showLightning = params.showLightning
	end
	-- showCharge
	if params.showCharge ~= nil and supportedParams.showCharge then
		assert(type(params.showCharge) == "boolean", "Invalid data type for 'showCharge'. A boolean was expected!")
		validatedParams.showCharge = params.showCharge
	end
	-- Vmax
	if params.Vmax ~= nil and supportedParams.Vmax then
		assert(type(params.Vmax) == "number", "Invalid data type for 'Vmax'. A number was expected!")
		validatedParams.Vmax = params.Vmax
	end
	-- Vmin
	if params.Vmin ~= nil and supportedParams.Vmin then
		assert(type(params.Vmin) == "number", "Invalid data type for 'Vmin'. A number was expected!")
		validatedParams.Vmin = params.Vmin
	end
	-- color
	if params.color ~= nil and supportedParams.color then
		assert(type(params.color) == "string", "Invalid data type for 'color'. A string was expected!")
		validatedParams.color = params.color
	end
	-- colorBg
	if params.colorBg ~= nil and supportedParams.colorBg then
		assert(type(params.colorBg) == "string", "Invalid data type for 'colorBg'. A string was expected!")
		validatedParams.colorBg = params.colorBg
	end
	-- showRails
	if params.showRails ~= nil and supportedParams.showRails then
		assert(type(params.showRails) == "boolean", "Invalid data type for 'showRails'. A boolean was expected!")
		validatedParams.showRails = params.showRails
	end
	-- buffer
	if params.buffer ~= nil and supportedParams.buffer then
		assert(type(params.buffer) == "boolean", "Invalid data type for 'buffer'. A boolean was expected!")
		validatedParams.buffer = params.buffer
	end

	-- Check user preferences

	-- DrawANSI
	validatedParams.drawANSI = Preferences:get('DrawANSI')

	-- Report unknown parameters
	for key in pairs(params) do
		assert(validatedParams[key] ~= nil, "Unknown parameter '" .. key .."'.")
	end

	return validatedParams
end

-- Helper function for drawing a table of Vectors
local function drawLines(x, y)
	assert(#x == #y, "Fatal error occurred, please report this to support@plexim.com")
	for k in ipairs(x) do
		Icon:line(x[k],y[k])
	end
end

-- Helper function for drawing an inversion bubble at (cx, cy). It is assumed that params has been validated before
local function drawBubble(cx, cy, r, params)
	local xC, yC = transform({Vector{cx}}, {Vector{cy}}, params)
	Icon:circle(xC[1][1], yC[1][1], r * params.scale)
end

-- Helper function for drawing an arc centered at (cx, cy), with the center, radii, and start/span adjusted for 90-degree rotation steps. It is assumed that params has been validated before
local function drawArc(cx, cy, rx, ry, start, span, params)
	local rot = params.rotate
	if rot == 90 or rot == 270 then rx, ry = ry, rx end
	local xC, yC = transform({Vector{cx}}, {Vector{cy}}, params)
	local s = math.fmod(math.fmod(start + rot, 360) + 360, 360)
	if rot == 90 or rot == 270 then span = -span end
	Icon:arc(xC[1][1], yC[1][1], rx * params.scale, ry * params.scale, s, span)
end

-- Calculates the state of charge (SoC) and the corresponding color based on the battery voltage (Vbat), maximum voltage (Vmax), and minimum voltage (Vmin).
local function getSoC(Vmax, Vmin, Vbat)
	local x = Vbat
	local m = (100 - 1) / (Vmax - Vmin)
	local b = 100 - m * Vmax
	local y = math.max(math.min(m * x + b, 100), 1)
	local color = 0

	if y <= 100 and y >= 75 then
		color = 'signal'

	elseif y < 75 and y >= 50 then
		color = 'event'

	elseif y < 50 and y >= 25 then
		color = 'magnetic'

	else
		color = {175,1,1}
	end

	return y,color
end

--?-------------------------------------------------------------------------------------------------------------------------------------------------------------
--? COMPONENTS FUNCTIONS
--?-------------------------------------------------------------------------------------------------------------------------------------------------------------
-- doubleFrame(70, 80, {color='thermal', colorBg='thermalBg'})
function list.doubleFrame(width, height, params)
	local params = validateInput(0, 0, params, 0, {color=true, colorBg=true})
	inset  = 2
   	radius = 4
	local color = params.color or 'text'
	local colorBg = params.colorBg

   	local hw = width  / 2
   	local hh = height / 2

   	-- Background patch
	if colorBg then
   		Icon:color(colorBg)
   		Icon:patch(
			{-hw+1, hw-1, hw-1, -hw+1},
   	   		{-hh+1, -hh+1, hh-1, hh-1})
	end

	local cx = hw - radius
	local cy = hh - radius

	local function DrawFrame(hw, hh, radius)
   	   	-- Horizontal lines
   	   	Icon:line({-cx + 1, cx - 1}, {-hh, -hh})
   	   	Icon:line({-cx + 1, cx - 1}, { hh,  hh})

   	   	-- Vertical lines
   	   	Icon:line({-hw, -hw}, {-cy + 1, cy - 1})
   	   	Icon:line({ hw,  hw}, {-cy + 1, cy - 1})

   	   	-- Corner arcs
   	   	Icon:arc(-cx, -cy, radius, radius,  90,  90)
   	   	Icon:arc( cx, -cy, radius, radius,  90, -90)
   	   	Icon:arc( cx,  cy, radius, radius,   0, -90)
   	   	Icon:arc(-cx,  cy, radius, radius, 180,  90)
	end

	-- Outer frame
	Icon:color(color)
   	DrawFrame(hw, hh, radius)

   	-- Inner frame
   	DrawFrame(hw - inset, hh - inset, radius - inset)

	-- Set the color back to the text color for any subsequent drawing
	Icon:color('text')
end

-- frame(70, 80)
function list.frame(width, height)
	local hw = width  / 2
	local hh = height / 2

	-- Frame
	Icon:line({-hw,  hw}, {-hh, -hh})
	Icon:line({-hw,  hw}, { hh,  hh})
	Icon:line({-hw, -hw}, {-hh,  hh})
	Icon:line({ hw,  hw}, {-hh,  hh})
end

-- resistor(-5, 5, {rotate=0, flip=false, wireLength={0, 0}, variable=false, flipArrow=false})
function list.resistor(x0, y0, params)
	local params = validateInput(x0, y0, params, 2, {variable=true, flipArrow=true})
	local wire = params.wireLength

	if params.drawANSI then
		local x = {Vector{            0,     0,   5, -5, 5, -5,  5,    0,            0}}
		local y = {Vector{-20 - wire[1], -12.5, -10, -5, 0,  5, 10, 12.5, 20 + wire[2]}}
		drawLines(transform(x, y, params))
	else
		local x = {Vector{  5,  5, -5,  -5,   5}, Vector{  0,             0}, Vector{ 0,            0}}
		local y = {Vector{-15, 15, 15, -15, -15}, Vector{-15, -20 - wire[1]}, Vector{15, 20 + wire[2]}}
		drawLines(transform(x, y, params))
	end

	-- Input terminal marker
	local xTerm, yTerm = transform({Vector{3.5}}, {Vector{-17.5}}, params)
	Icon:circle(xTerm[1][1], yTerm[1][1], 0.5 * params.scale)

	if params.variable then
		local x = {Vector{-10, 9.5}, Vector{7, 10, 9}}
		local y = {Vector{ 10, -9.5}, Vector{-9, -10, -7}}
		if params.flipArrow then
			for k in ipairs(x) do
				for i in ipairs(x[k]) do x[k][i] = x[k][i] * -1 end
			end
			for k in ipairs(y) do
				for i in ipairs(y[k]) do y[k][i] = y[k][i] * -1 end
			end
		end
		drawLines(transform(x, y, params))
	end
end

-- capacitor(-5, 5, {rotate=0, flip=false, wireLength={0, 0}, showPolarity=true, variable=false})
function list.capacitor(x0, y0, params)
	local params = validateInput(x0, y0, params, 2, {showPolarity=true, variable=true})
	local wire = params.wireLength
	if params.drawANSI then
		local x = {Vector{ -8, 8}, Vector{-8, -6, -2, 2, 6, 8}, Vector{0,              0}, Vector{0,            0}}
		local y = {Vector{-2, -2}, Vector{ 4,  3,  2, 2, 3, 4}, Vector{-2, -10 - wire[1]}, Vector{2, 10 + wire[2]}}
		drawLines(transform(x, y, params))
	else
		local x = {Vector{ 8, -8}, Vector{8, -8}, Vector{0,              0}, Vector{0,            0}}
		local y = {Vector{-2, -2}, Vector{2,  2}, Vector{-2, -10 - wire[1]}, Vector{2, 10 + wire[2]}}
		drawLines(transform(x, y, params))

		if params.showPolarity then
			local xMeas, yMeas = {Vector{4, 8}, Vector{6, 6}}, {Vector{-8, -8}, Vector{-10, -6}}
			drawLines(transform(xMeas, yMeas, params))
		end
	end

	if params.variable then
		local x = {Vector{-9.5, 9.5}, Vector{-7, -10, -9}}
		local y = {Vector{-9.5, 9.5}, Vector{-9, -10, -7}}
		drawLines(transform(x, y, params))
	end
end

-- resistorCapacitor(-5, 5, {rotate=0, flip=false, wireLength={0, 0}, variableResistor=false, variableCapacitor=false})
function list.resistorCapacitor(x0, y0, params)
	local params = validateInput(x0, y0, params, 2, {variableResistor=true, variableCapacitor=true})
	local wire = params.wireLength

	-- Capacitor branch
	local xCap, yCap = transform({Vector{0}}, {Vector{15}}, params)
	list.capacitor(xCap[1][1], yCap[1][1], {rotate=params.rotate + 90, scale=params.scale, flip=params.flip, wireLength=9, showPolarity=true, variable=params.variableCapacitor})

	-- Resistor branch
	local xRes, yRes = transform({Vector{0}}, {Vector{-15}}, params)
	list.resistor(xRes[1][1], yRes[1][1], {rotate=params.rotate + 270, scale=params.scale, flip=not params.flip, wireLength={0, 0}, variable=params.variableResistor, flipArrow=true})

	-- Connections
	local xConn = {Vector{-20 - wire[1], -20 - wire[1]}, Vector{20 + wire[2], 20 + wire[2]}}
	local yConn = {Vector{-15, 15}, Vector{-15, 15}}
	drawLines(transform(xConn, yConn, params))

	-- Terminal nodes
	local xNode, yNode = transform({Vector{-20 - wire[1], 20 + wire[2]}}, {Vector{0, 0}}, params)
	list.node(xNode[1][1], yNode[1][1])
	list.node(xNode[1][2], yNode[1][2])
end

-- inductor(-5, 5, {rotate=0, flip=false, wireLength={0, 0}, showArrow=true, flipArrow=false})
function list.inductor(x0, y0, params)
	local params = validateInput(x0, y0, params, 2, {showArrow=true, variable=true, flipArrow=true})
	local wire = params.wireLength

	-- draw wires
	local x = {Vector{            0,   0}, Vector{0,             0}}
	local y = {Vector{-20 - wire[1], -14}, Vector{14, 20 + wire[2]}}
	drawLines(transform(x, y, params))

	-- draw arcs and arc extensions
	local K, rot, flip = 1, params.rotate, params.flip
	local x_arc, y_arc, rx, ry, start, span = 0, 0, 3.5*K, 3.5*K, 90+rot, 180
	if start>360 then start=start-360 elseif start<0 then start=start+360 end
	if rot == 90 or rot == 270 then span = -span end
	local x_line, y_line = 0, 0
	for deltaY = -10.5*K, 10.5*K, 7*K do
		x_arc = {Vector{-1.5*K}}
		y_arc = {Vector{deltaY}}
		x_arc,y_arc = transform(x_arc,y_arc,params)
		Icon:arc(x_arc[1][1], y_arc[1][1], rx*params.scale, ry*params.scale, start, span)
	end
	for yPos = -14*K, 14*K, 7*K do
		drawLines(transform({Vector{0, -1.5*K}}, {Vector{yPos, yPos}}, params))
	end

	if params.showArrow then
		local xMeas, yMeas = {Vector{-2, 0, 2}}, {Vector{-16, -19, -16}}
		drawLines(transform(xMeas, yMeas, params))
	end

	if params.variable then
		local x = {Vector{-10, 9.5}, Vector{7, 10, 9}}
		local y = {Vector{ 10, -9.5}, Vector{-9, -10, -7}}
		if params.flipArrow then
			for k in ipairs(x) do
				for i in ipairs(x[k]) do x[k][i] = x[k][i] * -1 end
			end
			for k in ipairs(y) do
				for i in ipairs(y[k]) do y[k][i] = y[k][i] * -1 end
			end
		end
		drawLines(transform(x, y, params))
	end
end

-- resistorInductorSeries(-5, 5, {rotate=0, flip=false, wireLength={0, 0}, variableResistor=false, variableInductor=false})
function list.resistorInductorSeries(x0, y0, params)
	local params = validateInput(x0, y0, params, 2, {variableResistor=true, variableInductor=true})
	local wire = params.wireLength

	-- Resistor branch
	local xRes, yRes = transform({Vector{20}}, {Vector{0}}, params)
	list.resistor(xRes[1][1], yRes[1][1], {rotate=params.rotate + 270, scale=params.scale, flip=not params.flip, wireLength={wire[2], 0}, variable=params.variableResistor, flipArrow=true})

	-- Inductor branch
	local xInd, yInd = transform({Vector{-20}}, {Vector{0}}, params)
	list.inductor(xInd[1][1], yInd[1][1], {showArrow=true, rotate=params.rotate + 90, scale=params.scale, flip=not params.flip, wireLength={wire[1], -1}, variable=params.variableInductor})
end

-- resistorInductorParallel(-5, 5, {rotate=0, flip=false, wireLength={0, 0}, variableResistor=false, variableInductor=false})
function list.resistorInductorParallel(x0, y0, params)
	local params = validateInput(x0, y0, params, 2, {variableResistor=true, variableInductor=true})
	local wire = params.wireLength

	-- Inductor branch
	local xInd, yInd = transform({Vector{0}}, {Vector{16}}, params)
	list.inductor(xInd[1][1], yInd[1][1], {rotate=params.rotate + 90, scale=params.scale, flip=not params.flip, wireLength=0, showArrow=true, variable=params.variableInductor,flipArrow=true})

	-- Resistor branch
	local xRes, yRes = transform({Vector{0}}, {Vector{-15}}, params)
	list.resistor(xRes[1][1], yRes[1][1], {rotate=params.rotate + 270, scale=params.scale, flip=not params.flip, wireLength={0, 0}, variable=params.variableResistor, flipArrow=true})

	-- Connections
	local xConn = {Vector{-20 - wire[1], -20 - wire[1]}, Vector{20 + wire[2], 20 + wire[2]}}
	local yConn = {Vector{-15, 15}, Vector{-15, 15}}
	drawLines(transform(xConn, yConn, params))

	-- Terminal nodes
	local xNode, yNode = transform({Vector{-20 - wire[1], 20 + wire[2]}}, {Vector{0, 0}}, params)
	list.node(xNode[1][1], yNode[1][1])
	list.node(xNode[1][2], yNode[1][2])
end

-- transformer(-5, 5, {rotate=0, flip=false, wireLength={0, 0, 0, 0}, showCore=true, showPolarity=true, polarity="+-"})
function list.transformer(x0, y0, params)
	local params = validateInput(x0, y0, params, 4, {showPolarity=true, polarity=true, showCore=true})
	local wire = params.wireLength

	-- Primary winding
	local xShift, yShift = transform({Vector{-10}}, {Vector{0}}, params)
	list.inductor(xShift[1][1], yShift[1][1], {rotate=params.rotate+180, scale=params.scale, flip=params.flip, wireLength={wire[2], wire[1]}})

	-- Secondary winding
	xShift, yShift = transform({Vector{10}}, {Vector{0}}, params)
	list.inductor(xShift[1][1], yShift[1][1], {rotate=params.rotate, scale=params.scale, flip=params.flip, wireLength={wire[3], wire[4]}})

	-- magnetic core decoration
	if params.showCore then
		local xCore = {Vector{-1.5, -1.5}, Vector{1.5, 1.5}}
		local yCore = {Vector{ -15,   15}, Vector{-15,  15}}
		drawLines(transform(xCore, yCore, params))
	end

	-- polarity
	if params.showPolarity then
		local xPol1, xPol2, yPol1, yPol2
		if params.polarity == '+' or params.polarity == "++" then
			xPol1, yPol1 = transform({Vector{-6.0}}, {Vector{-18.0}}, params)
			xPol2, yPol2 = transform({Vector{ 6.5}}, {Vector{-17.5}}, params)
		elseif params.polarity == "-" or params.polarity == "--" then
			xPol1, yPol1 = transform({Vector{-6.0}}, {Vector{18.0}}, params)
			xPol2, yPol2 = transform({Vector{ 6.5}}, {Vector{17.5}}, params)
		elseif params.polarity == "+-" then
			xPol1, yPol1 = transform({Vector{-6.0}}, {Vector{-18.0}}, params)
			xPol2, yPol2 = transform({Vector{ 6.5}}, {Vector{17.5}}, params)
		elseif params.polarity == "-+" then
			xPol1, yPol1 = transform({Vector{-6.0}}, {Vector{18.0}}, params)
			xPol2, yPol2 = transform({Vector{ 6.5}}, {Vector{-17.5}}, params)
		else
			assert(false, "Unsupported 'polarity' (Use +, -, +-, or -+)")
		end
		Icon:circle(xPol1[1][1], yPol1[1][1], 1*params.scale, false)
		Icon:circle(xPol2[1][1], yPol2[1][1], 0.5*params.scale, false)
	end
end

-- Tline(-5, 5, {rotate=0, flip=false, wireLength={0, 0, 0, 0}})
function list.Tline(x0, y0, params)
	local params = validateInput(x0, y0, params, 4)
	local wire = params.wireLength

	-- top and bottom rails
	local x = {Vector{-25, 25}, Vector{-25, 25}}
	local y = {Vector{-10, -10}, Vector{10, 10}}
	drawLines(transform(x, y, params))

	-- leads with extension (top-left, bottom-left, top-right, bottom-right)
	local xLead = {Vector{-40 - wire[1], -37, -32, -25}, Vector{-40 - wire[2], -37, -32, -25}, Vector{40 + wire[3], 37, 32, 29}, Vector{40 + wire[4], 37, 32, 29}}
	local yLead = {Vector{           10,  10,   5,   5}, Vector{          -10, -10,  -5,  -5}, Vector{          10,  10,   5,   5}, Vector{          -10, -10,  -5,  -5}}
	drawLines(transform(xLead, yLead, params))

	-- polarity marker
	local xDot, yDot = transform({Vector{-32}}, {Vector{-12}}, params)
	Icon:circle(xDot[1][1], yDot[1][1], 0.5 * params.scale)

	-- rounded end caps
	local rot = params.rotate
	local rx, ry = 4 * params.scale, 10 * params.scale
	if rot == 90 or rot == 270 then rx, ry = ry, rx end

	local xCap1, yCap1 = transform({Vector{-25}}, {Vector{0}}, params)
	Icon:ellipse(xCap1[1][1], yCap1[1][1], rx, ry)

	local start = 270 + rot
	if start > 360 then start = start - 360 elseif start < 0 then start = start + 360 end
	local span = 180
	if rot == 90 or rot == 270 then span = -span end

	local xCap2, yCap2 = transform({Vector{25}}, {Vector{0}}, params)
	Icon:arc(xCap2[1][1], yCap2[1][1], rx, ry, start, span)
end

-- diode(-5, 5, {rotate=0, flip=false, wireLength={0, 0}, deviceType='gen'})
function list.diode(x0, y0, params)
	-- Note that changes to this function also affect the thyristor, the mosfetDiode, and the igbtDiode
	local params = validateInput(x0, y0, params, 2, {deviceType=true})
	local wire = params.wireLength

	-- draw the generic diode symbol
	local x = {Vector{-7, 7,  0, -7}, Vector{-7,  7}, Vector{ 0,             0}, Vector{0,            0}}
	local y = {Vector{ 6, 6, -6,  6}, Vector{-6, -6}, Vector{-6, -15 - wire[1]}, Vector{6, 15 + wire[2]}}
	drawLines(transform(x, y, params))

	local deviceType = params.deviceType or "gen"
	if deviceType == "gen" then
		-- general diode symbol

	elseif deviceType == "zen" then
		--	zener diode symbol
		local xZener = {Vector{-9, -7, -7, -7}, Vector{7, 7, 7, 9}}
		local yZener = {Vector{-3, -6, -6, -6}, Vector{-6, -6, -6, -9}}
		drawLines(transform(xZener, yZener, params))

	elseif deviceType == "sch" then
		-- schottky diode symbol
		local xSchottky = {Vector{-8, -9, -9, -7}, Vector{8, 9, 9, 7}}
		local ySchottky = {Vector{-6, -6, -3, -3}, Vector{-6, -6, -9, -9}}
		drawLines(transform(xSchottky, ySchottky, params))

	else
		assert(false, "Unsupported 'deviceType' (Use gen, zen, or sch)")

	end
end

-- thyristor(-5, 5, {rotate=0, flip=false, wireLength={0, 0, 0}})
function list.thyristor(x0, y0, params)
	local params = validateInput(x0, y0, params, 3)
	local wire = params.wireLength

	list.diode(params.x0, params.y0, {rotate=params.rotate, scale=params.scale, flip=params.flip, wireLength={wire[1], wire[3]}})

	local x = {Vector{ 0,  0, -4,  -7, -15 - wire[2]}}
	local y = {Vector{-6, -6, -6, -10,           -10}}
	drawLines(transform(x, y, params))
end

-- igbt(-5, 5, {rotate=0, flip=false, wireLength={0, 0, 0}, shiftGate=false})
function list.igbt(x0, y0, params)
	local params = validateInput(x0, y0, params, 3, {deviceType=true, shiftGate=true})
	local wire = params.wireLength
	local gateYOffset = params.shiftGate and 8 or 0

	local igbtType = params.deviceType or "n"
	local xArrow, xArrow
	if igbtType == "n" then
		xArrow = Vector{-5.650, -1.667, -3.864}
		yArrow = Vector{ 8.634,  9.000,  5.658}
	-- elseif igbtType == "p" then
	-- 	xArrow = Vector{-6.136, -8.333, -4.350}
	-- 	yArrow = Vector{ 8.342,  5.000,  5.366}
	else
		-- Support for deviceType 'p' was dropped in 5.0.3 since these devices are not available
		-- assert(false, "Unsupported 'deviceType' (Use n or p)")
		assert(false, "Unsupported 'deviceType' (Use n)")
	end

	local x = {Vector{            0,   0, -10, -10,  0,            0}, Vector{-10, -10}, Vector{-14, -14}, Vector{        -14, -20 - wire[2]}, xArrow}
	local y = {Vector{-20 - wire[1], -10,  -4,   4, 10, 20 + wire[3]}, Vector{ -8,   8}, Vector{ -8,   8}, Vector{gateYOffset,   gateYOffset}, yArrow}
	drawLines(transform(x, y, params))
end

-- igbtDiode(-5, 5, {rotate=0, flip=false, wireLength={0, 0, 0}, shiftGate=true})
function list.igbtDiode(x0, y0, params)
	local params = validateInput(x0, y0, params, 3, {deviceType=true, shiftGate=true})

	list.igbt(params.x0, params.y0, {rotate=params.rotate, scale=params.scale, flip=params.flip, wireLength={params.wireLength[1], params.wireLength[2], params.wireLength[3]}, deviceType=params.deviceType, shiftGate=params.shiftGate})

	-- Rotation of diode origin
	local xD, yD = transform({Vector{10}}, {Vector{0}}, params)
	local flipDiode = params.flip
	if params.deviceType == "p" then
		flipDiode = not flipDiode
	end
	list.diode(xD[1][1], yD[1][1], {rotate=params.rotate, scale=params.scale, flip=flipDiode, wireLength={-1, -1}})

	-- iGBT/diode connections
	local xConn = {Vector{  0,  10}, Vector{ 0, 10}}
	local yConn = {Vector{-14, -14}, Vector{14, 14}}
	drawLines(transform(xConn, yConn, params))
end

-- mosfet(-5, 5, {rotate=0, flip=false, wireLength={0, 0, 0}, deviceType="n", shiftGate=false})
function list.mosfet(x0, y0, params)
	local params = validateInput(x0, y0, params, 3, {deviceType=true, shiftGate=true})
	local wire = params.wireLength
	local gateYOffset = params.shiftGate and 10 or 0

	local mosType = params.deviceType or "n"
	local yArrow = Vector{-2, 0, 2}
	local xArrow
	if mosType == "n"then
		-- n-channel MOSFET
		xArrow = Vector{-4, -8, -4}

		-- p-channel MOSFET
	elseif mosType == "p" then
		xArrow = Vector{-8, -4, -8}

	else
		assert(false, "Unsupported 'deviceType' (Use n or p)")
	end

	-- draw the generic MOSFET symbol
	local x = {Vector{            0,   0, -10}, Vector{-10, -10}, Vector{-10, -10}, Vector{-10, -10}, Vector{-10, 0,  0}, Vector{-10,  0,            0}, Vector{-15, -15}, Vector{        -15, -20 - wire[2]}, xArrow}
	local y = {Vector{-20 - wire[1], -10, -10}, Vector{-13,  -7}, Vector{ -3,   3}, Vector{  7,  13}, Vector{  0, 0, 10}, Vector{ 10, 10, 20 + wire[3]}, Vector{-10,  10}, Vector{gateYOffset,   gateYOffset}, yArrow}
	drawLines(transform(x, y, params))
end

-- mosfetDiode(-5, 5, {rotate=0, flip=false, wireLength={0, 0, 0}, deviceType="p", shiftGate=true})
function list.mosfetDiode(x0, y0, params)
	local params = validateInput(x0, y0, params, 3, {deviceType=true, shiftGate=true})

	list.mosfet(params.x0, params.y0, {rotate=params.rotate, scale=params.scale, flip=params.flip, wireLength={params.wireLength[1], params.wireLength[2], params.wireLength[3]}, deviceType=params.deviceType, shiftGate=params.shiftGate})

	-- Rotation of diode origin
	local xD, yD = transform({Vector{12}}, {Vector{0}}, params)
	local flipDiode = params.flip
	if params.deviceType == "p" then
		flipDiode = not flipDiode
	end
	list.diode(xD[1][1], yD[1][1], {rotate=params.rotate, scale=params.scale, flip=flipDiode, wireLength={-1, -1}})

	-- mosfet/diode connections
	local xConn = {Vector{  0,  12}, Vector{ 0, 12}}
	local yConn = {Vector{-14, -14}, Vector{14, 14}}
	drawLines(transform(xConn, yConn, params))
end

-- hemt(-5, 5, {rotate=0, flip=false, wireLength={0, 0, 0}, deviceType="n"})
function list.hemt(x0, y0, params)
	local params = validateInput(x0, y0, params, 3)
	local wire = params.wireLength

	local yArrow = Vector{14, 12, 10}
	local xArrow = Vector{-2, 2, -2}

	local x = {Vector{5, 5, -6}, Vector{-6, -6}, Vector{-7, -7}, Vector{-6, -6}, Vector{-7, -7}, Vector{-6, -6}, Vector{-7, -7}, Vector{-7, -20 - wire[2]}, Vector{5, 5, -6}, xArrow}
	local y = {Vector{-20 - wire[1], -10, -10}, Vector{14, 10}, Vector{14, 10}, Vector{4, 6}, Vector{4, 6}, Vector{0, -12}, Vector{0, -12}, Vector{5, 5}, Vector{20 + wire[3], 12, 12}, yArrow}
	drawLines(transform(x, y, params))

	--! original code from Texas Instruments, which is not used anymore since the arrow is now drawn as part of the main icon
	--local x = {Vector{5, 5, -6}, Vector{-6, -6}, Vector{-7, -7}, Vector{-6, -6}, Vector{-7, -7}, Vector{-6, -6}, Vector{-7, -7}, Vector{-7, -20 - wire[2]}, Vector{5, 5, -6}}
	--local y = {Vector{-20 - wire[1], -10, -10}, Vector{14, 10}, Vector{14, 10}, Vector{4, 6}, Vector{4, 6}, Vector{0, -12}, Vector{0, -12}, Vector{5, 5}, Vector{20 + wire[3], 12, 12}}
	--drawLines(transform(x, y, params))

	--local xPatch, yPatch = transform({Vector{-2, 2, -2}}, {Vector{14, 12, 10}}, params)
	--Icon:patch(xPatch[1], yPatch[1])
end

-- bjt(-5, 5, {rotate=0, flip=false, wireLength={0, 0, 0}, deviceType="npn"})
function list.bjt(x0, y0, params)
	local params = validateInput(x0, y0, params, 3, {deviceType=true})
	local wire = params.wireLength

	local bjtType = params.deviceType or "npn"
	local xArrow, xArrow
	if bjtType == "npn" then
		xArrow = Vector{-5.650, -1.667, -3.864}
		yArrow = Vector{ 8.634,  9.000,  5.658}
	elseif bjtType == "pnp" then
		xArrow = Vector{-6.136, -8.333, -4.350}
		yArrow = Vector{ 8.342,  5.000,  5.366}
	else
		assert(false, "Unsupported 'deviceType' (Use npn or pnp)")
	end

	local x = {Vector{            0,   0, -10, -10,  0,            0}, Vector{-10, -10}, Vector{-10, -20 - wire[2]}, xArrow}
	local y = {Vector{-20 - wire[1], -10,  -4,   4, 10, 20 + wire[3]}, Vector{ -8,   8}, Vector{  0,             0}, yArrow}
	drawLines(transform(x, y, params))
end

-- jfet(-5, 5, {rotate=0, flip=false, wireLength={0, 0, 0}, deviceType="n", shiftGate=false})
function list.jfet(x0, y0, params)
	local params = validateInput(x0, y0, params, 3, {deviceType=true, shiftGate=true})
	local wire = params.wireLength
	local gateYOffset = params.shiftGate and 10 or 0

	local jfetType = params.deviceType or "n"
	local xArrow, xArrow
	if jfetType == "n" then
		xArrow = Vector{-16, -12, -16}
		yArrow = Vector{  2,   0,  -2} + gateYOffset
	elseif jfetType == "p" then
		xArrow = Vector{-12, -16, -12}
		yArrow = Vector{  2,   0,  -2} + gateYOffset
	else
		assert(false, "Unsupported 'deviceType' (Use n or p)")
	end

	local x = {Vector{            0,   0, -10, -10,  0,            0}, Vector{-10, -10}, Vector{        -10, -20 - wire[2]}, xArrow}
	local y = {Vector{-20 - wire[1], -10, -10,  10, 10, 20 + wire[3]}, Vector{-12,  12}, Vector{gateYOffset,   gateYOffset}, yArrow}
	drawLines(transform(x, y, params))
end

function list.node(x0,y0)
	Icon:circle(x0,y0,1.25,true)
end

-- ground(-5, 5, {rotate=0, flip=false, wireLength=0, deviceType='power'})
function list.ground(x0, y0, params)
	local params = validateInput(x0, y0, params, 1, {deviceType=true})
	params.rotate = math.fmod(params.rotate + 180, 360) -- point the symbol down by default
	local wire = params.wireLength
	local deviceType = params.deviceType or "power"

	-- GND bar, centered at (0,0), with a wire stub (default length 3, extendable via wireLength)
	local x = {Vector{-8, 8}, Vector{0, 0}}
	local y = {Vector{0, 0}, Vector{0, 3 + wire[1]}}
	drawLines(transform(x, y, params))

	if deviceType == "power" then
		-- power ground symbol (single bar, drawn above)
	elseif deviceType == "signal" then
		-- signal ground symbol
		local xSignal = {Vector{-5, 5}, Vector{-2, 2}}
		local ySignal = {Vector{-4, -4}, Vector{-8, -8}}
		drawLines(transform(xSignal, ySignal, params))
	else
		assert(false, "Unsupported 'deviceType' (Use power or signal)")
	end
end

-- switch2(-5, 5, {rotate=0, flip=false, wireLength={0, 0}, switchClosed=0})
function list.switch(x0, y0, params)
	local params = validateInput(x0, y0, params, 2, {switchClosed=1})
	local wire = params.wireLength
	local switchClosed = params.switchClosed or 0

	local xBlade, yBlade
	if switchClosed == 1 then
		xBlade = Vector{-11, 11}
		yBlade = Vector{-3.95, -3.95}
	else
		xBlade = Vector{11, -11}
		yBlade = Vector{-3.95, 3.95}
	end

	local x = {Vector{-11, -15.1 - wire[1]}, Vector{11, 15.1 + wire[2]}, xBlade}
	local y = {Vector{-3.95, -3.95}, Vector{-3.95, -3.95}, yBlade}
	drawLines(transform(x, y, params))
end

-- voltageSource(-5, 5, {rotate=0, flip=false, wireLength={0, 0}})
function list.voltageSource(x0, y0, params)
	local params = validateInput(x0, y0, params, 2)
	local wire = params.wireLength

	-- Circle body
	local xBody, yBody = transform({Vector{0}}, {Vector{0}}, params)
	Icon:circle(xBody[1][1], yBody[1][1], 10 * params.scale)

	-- Polarity markings
	local xPlus,  yPlus  = transform({Vector{0}}, {Vector{-6}}, params)
	local xMinus, yMinus = transform({Vector{0}}, {Vector{ 4}}, params)
	Icon:text(xPlus[1][1],  yPlus[1][1],  '+','FontSize', 11 * params.scale)
	Icon:text(xMinus[1][1], yMinus[1][1], '-','FontSize', 11 * params.scale)

	-- Upper and lower wires with extension
	local x = {Vector{0,  0}, Vector{0,   0}}
	local y = {Vector{10, 15.2 + wire[1]}, Vector{-10, -15.2 - wire[2]}}
	drawLines(transform(x, y, params))
end

-- arrow(-5, 5, {rotate=0, flip=false})
function list.arrow(x0, y0, params)
	local params = validateInput(x0, y0, params, 0)

	local x = {Vector{0, 0}, Vector{-2, 0, 2}}
	local y = {Vector{7, -7}, Vector{-4, -7, -4}}
	drawLines(transform(x, y, params))
end

-- arrowHead(-5, 5, {rotate=0, flip=false})
function list.arrowHead(x0, y0, params)
	local params = validateInput(x0, y0, params, 0)

	local x = {Vector{-2, 0, 2}}
	local y = {Vector{1.5, -1.5, 1.5}}
	drawLines(transform(x, y, params))
end

-- signals(-5, 5, {rotate=0, flip=false, deviceType='clock'})
function list.signals(x0, y0, params)
	local params = validateInput(x0, y0, params, 0, {deviceType=true})
	local deviceType = params.deviceType or "clock"

	if deviceType == "clock" then
		local x = {Vector{ -2.25, -2.25}, Vector{-2.25,  2.25}, Vector{2.25,  2.25}, Vector{ 2.25, 11.25}, Vector{-6.75, -2.25}, Vector{-6.75, -6.75}, Vector{-11.25, -6.75}}
		local y = {Vector{   4.5,   -4.5}, Vector{-4.5,   -4.5}, Vector{ 4.5,   -4.5}, Vector{  4.5,   4.5}, Vector{  4.5,   4.5}, Vector{  4.5,   -4.5}, Vector{  -4.5,   -4.5}}
		drawLines(transform(x, y, params))
	elseif deviceType == "pulse" then
		local x = {Vector{-4.5, -4.5}, Vector{-4.5,    0}, Vector{   0,    0}, Vector{  0,   9}, Vector{-9, -4.5}}
		local y = {Vector{ 4.5,  -4.5}, Vector{-4.5, -4.5}, Vector{ 4.5, -4.5}, Vector{4.5, 4.5}, Vector{4.5,  4.5}}
		drawLines(transform(x, y, params))
	elseif deviceType == "sine" then
		local x = {Vector{-12, -11, -10, -9.5, -9, -8.5, -8, -7, -5, -4, -3.5, -3, -2.5, -2, -1, 1, 2, 2.5, 3, 3.5, 4, 5, 7, 8, 8.5, 9, 9.5, 10, 11, 12}}
		local y = {Vector{0, -2.5, -4.33, -4.83, -5, -4.83, -4.33, -2.5, 2.5, 4.33, 4.83, 5, 4.83, 4.33, 2.5, -2.5, -4.33, -4.83, -5, -4.83, -4.33, -2.5, 2.5, 4.33, 4.83, 5, 4.83, 4.33, 2.5, 0}}
		drawLines(transform(x, y, params))
	elseif deviceType == "noise" then
		local x = {Vector{-12, -10, -10, -8, -8, -6, -6, -4, -4, -2, -2, 0, 0, 2, 2, 4, 4, 6, 6, 8, 8, 10, 10, 12}}
		local y = {Vector{1.5, 1.5, -3.5, -3.5, -0.5, -0.5, 8.5, 8.5, -8.5, -8.5, 5.5, 5.5, -1.5, -1.5, 2.5, 2.5, -3.5, -3.5, -2.5, -2.5, 3.5, 3.5, -0.5, -0.5}}
		drawLines(transform(x, y, params))
	elseif deviceType == "counter" then
		local x = {Vector{-13.5, -10.5, -10.5, -6.5, -6.5, -2.5, -2.5, 1.5, 1.5, 5.5, 5.5, 9.5, 9.5, 13.5, 13.5, 13.5}}
		local y = {Vector{6, 6, 2, 2, -2, -2, -6, -6, 6, 6, 2, 2, -2, -2, -6, -6}}
		drawLines(transform(x, y, params))
	elseif deviceType == "impulse" then
		local x = {Vector{0, 0}}
		local y = {Vector{-9, 9}}
		drawLines(transform(x, y, params))
	else
		assert(false, "Unsupported 'deviceType' (Use clock, pulse, sine, noise, counter, or impulse)")
	end
end

-- axis(-5, 5, {rotate=0, flip=false, wireLength={0, 0, 0, 0}})
function list.axis(x0, y0, params)
	local params = validateInput(x0, y0, params, 4)
	local wire = params.wireLength

	local x = {Vector{-13 - wire[1], 13 + wire[2]}, Vector{-11, -11}}
	local y = {Vector{ 11, 11}, Vector{-13 - wire[3], 13 + wire[4]}}
	drawLines(transform(x, y, params))
end

-- gates(-5, 5, {rotate=0, flip=false, deviceType='and'})
function list.gates(x0, y0, params)
	local params = validateInput(x0, y0, params, 0, {deviceType=true})
	local deviceType = params.deviceType or "and"

	if deviceType == "and" then
		local x = {Vector{-15, -15}, Vector{-0.1, -15}, Vector{-0.1, -15}}
		local y = {Vector{-15,  15}, Vector{ -15, -15}, Vector{  15,  15}}
		drawLines(transform(x, y, params))
		drawArc(0, 0, 15, 15, 90, -180, params)

	elseif deviceType == "nand" then
		local x = {Vector{-15, -15}, Vector{-0.1, -15}, Vector{-0.1, -15}}
		local y = {Vector{-15,  15}, Vector{ -15, -15}, Vector{  15,  15}}
		drawLines(transform(x, y, params))
		drawArc(0, 0, 15, 15, 90, -180, params)
		drawBubble(17, 0, 2, params)

	elseif deviceType == "or" then
		local x = {Vector{-15, -0.1}, Vector{-15, -0.1}}
		local y = {Vector{ 15,   15}, Vector{-15, -15}}
		drawLines(transform(x, y, params))
		drawArc(0, 0, 15, 15, 90, -180, params)
		drawArc(-35, 0, 25, 25, -36.87, 73.74, params)

	elseif deviceType == "nor" then
		local x = {Vector{-15, -0.1}, Vector{-15, -0.1}}
		local y = {Vector{ 15,   15}, Vector{-15, -15}}
		drawLines(transform(x, y, params))
		drawArc(0, 0, 15, 15, 90, -180, params)
		drawArc(-35, 0, 25, 25, -36.87, 73.74, params)
		drawBubble(17, 0, 2, params)

	elseif deviceType == "xor" then
		local x = {Vector{-15, -0.1}, Vector{-15, -0.1}}
		local y = {Vector{ 15,   15}, Vector{-15, -15}}
		drawLines(transform(x, y, params))
		drawArc(0, 0, 15, 15, 90, -180, params)
		drawArc(-35, 0, 25, 25, -36.87, 73.74, params)
		drawArc(-39, 0, 25, 25, -36.87, 73.74, params)

	elseif deviceType == "xnor" then
		local x = {Vector{-15, -0.1}, Vector{-15, -0.1}}
		local y = {Vector{ 15,   15}, Vector{-15, -15}}
		drawLines(transform(x, y, params))
		drawArc(0, 0, 15, 15, 90, -180, params)
		drawArc(-35, 0, 25, 25, -36.87, 73.74, params)
		drawArc(-39, 0, 25, 25, -36.87, 73.74, params)
		drawBubble(17, 0, 2, params)

	elseif deviceType == "not" then
		local x = {Vector{-15, -15, 15, -15}}
		local y = {Vector{ 15, -15,  0,  15}}
		drawLines(transform(x, y, params))
		drawBubble(17, 0, 2, params)

	elseif deviceType == "buffer" then
		local x = {Vector{-15, -15, 15, -15}}
		local y = {Vector{ 15, -15,  0,  15}}
		drawLines(transform(x, y, params))

	else
		assert(false, "Unsupported 'deviceType' (Use and, nand, or, nor, xor, xnor, not or buffer)")
	end
end

-- hysteresis(-5, 5, {rotate=0, flip=false})
function list.hysteresis(x0, y0, params)
	local params = validateInput(x0, y0, params, 0)

	local x = {Vector{-12, -9, 3, 12}, Vector{-12, -3, 9, 12}}
	local y = {Vector{  6,  6, -6, -6}, Vector{  6,  6, -6, -6}}
	drawLines(transform(x, y, params))
end

-- currentSource(-5, 5, {rotate=0, flip=false, wireLength={0, 0}})
function list.currentSource(x0, y0, params)
	local params = validateInput(x0, y0, params, 2)
	local wire = params.wireLength

	-- Circle body
	local xBody, yBody = transform({Vector{0}}, {Vector{0}}, params)
	Icon:circle(xBody[1][1], yBody[1][1], 10 * params.scale)

	-- Arrow
	list.arrow(params.x0, params.y0, {rotate=params.rotate, scale=params.scale, flip=params.flip})

	-- Upper and lower wires with extension
	local xWire = {Vector{0,  0}, Vector{0,   0}}
	local yWire = {Vector{10, 15.2 + wire[1]}, Vector{-10, -15.2 - wire[2]}}
	drawLines(transform(xWire, yWire, params))
end

-- battery(-5, 5, {rotate=0, flip=false, wireLength={0, 0}, showLightning=true, showCharge=true, Vmax=15, Vmin=8})
function list.battery(x0, y0, params)
	local params = validateInput(x0, y0, params, 2, {showLightning=true, showCharge=true, Vmax=true, Vmin=true})
	local wire = params.wireLength
	local W, H, L = 2.5, 7.5, 4

	local showLightning = params.showLightning
	if showLightning == nil then showLightning = true end

	local showCharge = params.showCharge
	if showCharge == nil then showCharge = true end

	local Vmax = params.Vmax or 15
	local Vmin = params.Vmin or 8
	local VbatDefault = Vmin + (74 / 99) * (Vmax - Vmin) -- Corresponds to soc = 75
	local ok, Vbat = pcall(function() return eval(Dialog:get('V_bat')) end)
	Vbat = math.max(ok and Vbat or VbatDefault, Vmin)
	local soc, color = getSoC(Vmax, Vmin, Vbat)

	-- Main frame and leads
	local x = {Vector{-W, W, W, -W, -W} * L, Vector{0,                 0}, Vector{0,                0}}
	local y = {Vector{ H, H, -H, -H,  H} * L, Vector{-H * L, -H * L - wire[1]}, Vector{H * L, H * L + wire[2]}}
	drawLines(transform(x, y, params))

	-- Charge level
	if showCharge then
		Icon:color(color)
		local xCharge, yCharge = transform({Vector{-W, W, W, -W, -W} * L * 0.9}, {Vector{H, H, -H, -H, H} * L * (soc / 100 * 0.96) + (100 - soc) / 100 * H * L}, params)
		Icon:patch(xCharge[1], yCharge[1])
	end

	-- Tip
	Icon:color('text')
	local xTip, yTip = transform({Vector{-W / 2, W / 2, W / 2, -W / 2, -W / 2} * L}, {Vector{-H, -H, -H * 1.1, -H * 1.1, -H} * L}, params)
	Icon:patch(xTip[1], yTip[1])

	-- Lightning bolt
	if showLightning then
		local xBolt, yBolt = transform({Vector{0, 0.5, -1, 0, -0.5, 1, 0} * -1 * L}, {Vector{-0.2, -1, 0.2, 0.2, 1, -0.2, -0.2} * 3 * L + 0.5 * H}, params)
		Icon:patch(xBolt[1], yBolt[1])
	end

	-- Polarity markings
	local xPlus,  yPlus  = transform({Vector{0}}, {Vector{-H * 0.75 * L}}, params)
	local xMinus, yMinus = transform({Vector{0}}, {Vector{ H * 0.75 * L}}, params)
	Icon:text(xPlus[1][1],  yPlus[1][1],  '+', 'FontSize', 20 * params.scale)
	Icon:text(xMinus[1][1], yMinus[1][1], '-', 'FontSize', 20 * params.scale)
end

-- shunt(-5, 5, {rotate=0, flip=false, wireLength={0, 0}})
function list.shunt(x0, y0, params)
	local params = validateInput(x0, y0, params, 2, {})
	local wire = params.wireLength

	local x = {Vector{0, 0, 5, -5, 5, -5, 5, 0, 0}}
	local y = {Vector{-15 - wire[1], -13, -10, -5, 0, 5, 10, 13, 15 + wire[2]}}
	drawLines(transform(x, y, params))

	local xTerm, yTerm = transform({Vector{-3.5}}, {Vector{-15}}, params)
	Icon:circle(xTerm[1][1], yTerm[1][1], 0.5 * params.scale)
end

-- opamp(-5, 5, {rotate=0, flip=false, scale=1, wireLength={0, 0, 0}, deviceType="ana", showRails=true, showPolarity=true, buffer=false})
function list.opamp(x0, y0, params)
	local params = validateInput(x0, y0, params, 3, {deviceType=true, showRails=true, showPolarity=true, buffer=true})
	local wire = params.wireLength
	local deviceType = params.deviceType or "ana"

	local showRails = params.showRails
	if showRails == nil then showRails = false end

	local showPolarity = params.showPolarity
	if showPolarity == nil then showPolarity = true end

	local buffer = params.buffer
	if buffer == nil then buffer = false end

	-- opamp body
	local x = {Vector{-20, -20,  20, -20}, Vector{-20, -20 - wire[1]}, Vector{-20, -20 - wire[2]}, Vector{20, 20 + wire[3]}}
	local y = {Vector{ 20, -20,   0,  20}, Vector{-10,        -10}, Vector{ 10,         10}, Vector{ 0,         0}}
	drawLines(transform(x, y, params))

	if showRails then
		if deviceType == "ana" then
			-- Indicates an analog-type opamp like a buffer
			local xSat = {Vector{-10, -7, -3, 0}}
			local ySat = {Vector{  5,  5, -5, -5}}
			drawLines(transform(xSat, ySat, params))

			-- Indicates an digital-type opamp like a comparator
		elseif deviceType == "dig" then
			local xDig = {Vector{-10.5, -10.5}, Vector{-10.5, -6}, Vector{-6, -6}, Vector{-6, 3}, Vector{-15, -10.5}}
			local yDig = {Vector{4.5, -4.5}, Vector{-4.5, -4.5}, Vector{4.5, -4.5}, Vector{4.5, 4.5}, Vector{4.5, 4.5}}
			drawLines(transform(xDig, yDig, params))
		else
			assert(false, "Unsupported 'deviceType' (Use ana or dig)")
		end
	end

	-- show the input polarity signs
	if showPolarity then
		local xPlus, yPlus = transform({Vector{-14}}, {Vector{-10}}, params)
		Icon:text(xPlus[1][1], yPlus[1][1], '+', 'FontSize', 11 * params.scale)
		if not buffer then
			-- in case of unity buffer hide the negative polarity sign
			local xMinus, yMinus = transform({Vector{-14}}, {Vector{ 10}}, params)
			Icon:text(xMinus[1][1], yMinus[1][1], '-', 'FontSize', 11 * params.scale)
		end
	end
end

----------------------------------------------------------------------------------------------------------------------------------------------------------------
return list
