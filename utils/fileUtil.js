import fs from "fs"
function createFile(filePath) {
  if (!fs.existsSync(filePath)) {
    writeFile(filePath, "")
  }
}

function writeFile(filePath, content) {
  fs.writeFile(filePath, content, error => {
    if (error) {
      throw new Error(`${filePath}:写入${content}失败`)
    }
  })
}

function appendFile(filePath, content) {
  fs.appendFile(filePath, content, error => {
    if (error) {
      throw new Error(`${filePath}:追加${content}失败`)
    }
  })
}

function appendFileSync(filePath, content) {
  fs.appendFileSync(filePath, content, error => {
    if (error) {
      throw new Error(`${filePath}:同步追加${content}失败`)
    }
  })
}

export { createFile, writeFile, appendFile, appendFileSync }
