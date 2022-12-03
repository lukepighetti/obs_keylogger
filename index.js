const MQTT_HOST = process.env['MQTT_HOST']

const mqtt = require('mqtt')
const client = mqtt.connect('', { hostname: MQTT_HOST, port: 9001, protocol: 'ws' })
const debug = false

console.log(`connecting to broker ${MQTT_HOST}`)

client.on('connect', function() {
  console.log(`connected to broker ${MQTT_HOST}`)
  client.subscribe('obs_keylogger/macbook', function(err, granted) {
    if (err != null) {
      console.log(err);
    } else {
      console.log(granted);
    }
  })
})

client.on('message', function(topic, buffer) {
  const events = document.querySelector("#events")
  let message = buffer.toString();
  let isCount = message.startsWith("+") && message.length > 1
  if (!isCount) {
    const textNode = document.createTextNode(message)
    const spanNode = document.createElement('span')
    let isMulti = message.length > 1
    spanNode.className = isMulti ? 'multi' : 'char'
    spanNode.appendChild(textNode)
    events.appendChild(spanNode)
  } else {
    let count = message.replace('+', '')
    const lastNode = events.children[events.children.length - 1]
    const textNode = document.createTextNode(count)
    if (lastNode.className == 'count') {
      lastNode.replaceChildren(textNode)
    } else {
      const spanNode = document.createElement('span')
      spanNode.className = 'count'
      spanNode.appendChild(textNode)
      events.appendChild(spanNode)
    }
  }
  if (debug) console.log(`[${topic}]: ${message.toString()}`)
})