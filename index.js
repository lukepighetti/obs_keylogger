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

function setOpacityTimeout(spanId) {
  let el = document.querySelector("#" + spanId)
  let oldTimeoutId = timers[spanId]
  if (oldTimeoutId !== undefined) {
    el.style.opacity = 1
    clearTimeout(oldTimeoutId)
  }
  let newTimeoutId = setTimeout(() => {
    el.style.opacity = 0
  }, 10 * 1000)
  timers[spanId] = newTimeoutId
}

let timers = {}
let spanCount = 0;
client.on('message', function(topic, buffer) {
  const events = document.querySelector("#events")
  let message = buffer.toString();
  let isCount = message.startsWith("+") && message.length > 1
  if (!isCount) {
    const textNode = document.createTextNode(message)
    const spanNode = document.createElement('span')
    spanNode.appendChild(textNode)
    let isMulti = message.length > 1
    spanNode.className = isMulti ? 'multi' : 'char'
    spanNode.id = `span-${spanCount}`
    spanCount++
    events.appendChild(spanNode)
    setOpacityTimeout(spanNode.id)
  } else {
    let count = message.replace('+', '')
    const lastOuterNode = events.children[events.children.length - 1]
    setOpacityTimeout(lastOuterNode.id)
    const lastNode = lastOuterNode?.children[lastOuterNode?.children.length - 1]
    const textNode = document.createTextNode(count)
    if (lastNode === undefined) {
      const spanNode = document.createElement('span')
      spanNode.className = 'count'
      spanNode.appendChild(textNode)
      lastOuterNode?.appendChild(spanNode)
    } else {
      lastNode.replaceChildren(textNode)
    }
  }
  if (debug) console.log(`[${topic}]: ${message.toString()}`)
})

function reflow_animation(el) {
  if (el === undefined) return
  el.style.animation = 'none'
  el.offsetHeight; /* trigger reflow */
  el.style.animation = null
}
