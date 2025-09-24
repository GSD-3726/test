
function getDateString(date) {
  return `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, "0")}${String(date.getDate()).padStart(2, "0")}`
}

function getTimeString(date) {
  return `${String(date.getHours()).padStart(2, "0")}${String(date.getMinutes()).padStart(2, "0")}${String(date.getSeconds()).padStart(2, "0")}`
}

function getDateTimeString(date) {
  return `${getDateString(date)}${getTimeString(date)}`
}

export { getDateString, getTimeString, getDateTimeString }
