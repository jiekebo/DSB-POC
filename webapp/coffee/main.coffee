createGuid = ->
  "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace /[xy]/g, (c) ->
    r = Math.random() * 16 | 0
    v = (if c is "x" then r else (r & 0x3 | 0x8))
    v.toString 16

console.log("testing")
width = 960
height = 500
svg = d3.select("body").append("svg").attr("width", width).attr("height", height)
force = d3.layout.force().gravity(.05).distance(100).charge(-100).size([
  width
  height
])
ws = new WebSocket("ws://localhost:8888/ws?id=" + createGuid())
ws.onopen = ->
  ws.send "Message to send" 
  return

ws.onmessage = (evt) ->
  received_msg = evt.data
  obj = JSON.parse(received_msg)
  train = obj[0]
  stations = train.stations
  edges = train.edges
  links = []
  edges.forEach (edge) ->
    source = edge.start
    target = edge.end
    sourceId = 0
    targetId = 0
    i = 0

    while i < stations.length
      o = stations[i]
      if o.UIC is source
        sourceId = i
      else targetId = i  if o.UIC is target
      i++
    links.push
      source: sourceId
      target: targetId

    return

  force.nodes(stations).links(links).start()
  link = svg.selectAll(".link").data(links).enter().append("line").attr("class", "link")
  node = svg.selectAll(".node").data(stations).enter().append("g").attr("class", "node").call(force.drag)
  node.append("image").attr("xlink:href", "https://github.com/favicon.ico").attr("x", -8).attr("y", -8).attr("width", 16).attr "height", 16
  node.append("text").attr("dx", 12).attr("dy", ".35em").text (d) ->
    d.name

  force.on "tick", ->
    link.attr("x1", (d) ->
      d.source.x
    ).attr("y1", (d) ->
      d.source.y
    ).attr("x2", (d) ->
      d.target.x
    ).attr "y2", (d) ->
      d.target.y

    node.attr "transform", (d) ->
      "translate(" + d.x + "," + d.y + ")"

    return

  return

ws.onclose = ->
  ws.close()
  alert "Connection is closed..."
  return