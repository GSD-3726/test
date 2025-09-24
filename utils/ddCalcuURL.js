const list = {
  // h5端修改频繁，现已失效
  "h5": {
    // 第11位字符
    "keys": "yzwxcdabgh",
    // 第5 8 14位字母对应下标0 1 3的字符
    "words": ['z', 'y', '0', 'w'],
    // 第11位字符替换位置,从0开始
    "thirdReplaceIndex": 1,
    // 加密后链接后缀
    "suffix": "&sv=10000&ct=www"
  },
  "android": {
    "keys": "cdabyzwxkl",
    "words": ['x', 'a', '0', 'a'],
    "thirdReplaceIndex": 6,
    "suffix": "&sv=10004&ct=android"
  }
}

const importObj = {
  a: {
    a: (a, b, c) => { },
    b: (a) => { return 0 },
    c: () => { },
    d: (a, b, c, d) => { return 0 },
    e: (a) => { return 0 },
    f: (a, b, c, d, e) => { return 0 },
    g: (a, b) => { return 0 },
    h: (a, b) => { return 0 },
    i: (a) => { return 0 },
    j: (a, b, c, d, e) => { return 0 }
  }
}

/**
 * 加密url
 * @param {string} videoURL - 视频url
 * @param {Uint8Array} memoryView - 内存
 * @param {Function} getEncrypt - 加密方法
 * @returns {string} - 加密地址
 */
function encrypt(videoURL, memoryView, getEncrypt) {
  // 将地址写入内存
  let i;
  for (i = 0; i < videoURL.length; ++i) {
    memoryView[i] = videoURL.charCodeAt(i)
  }
  memoryView[i] = 0

  // 加密内存中的url
  let start = getEncrypt(0)

  // 从内存中读取加密后的url
  let encryptedURL = ""
  for (let i = start; memoryView[i] != 0; ++i) {
    encryptedURL += String.fromCharCode(memoryView[i])
  }
  return encryptedURL
}


/**
 * 初始化wasm
 * @param {string} masmURL - wasm地址
 * @returns {object} - wasm导出的内容
 */
async function initWasm(masmURL) {
  // 获取wasm文件
  let resp = await fetch(masmURL);
  // 初始化
  let { instance } = await WebAssembly.instantiateStreaming(resp, importObj)
  return instance.exports;
}



/**
 * 获取加密url
 * @param {object} exports - wasm导出的内容
 * @param {string} videoURL - 视频地址
 * @returns {string} - 播放地址
 */
function getEncryptURL(exports, videoURL) {
  // 获得内存
  const memory = exports.k
  const memoryView = new Uint8Array(memory.buffer)

  // 获取加密方法
  const getEncrypt = exports.m
  return encrypt(videoURL, memoryView, getEncrypt)
}


/**
 * h5端现已失效
 * 获取ddCalcu
 * 大致思路:把puData最后一个字符和第一个字符拼接，然后拼接倒数第二个跟第二个，一直循环，当第1 2 3 4次(从0开始)循环时需要插入特殊标识字符
 * 特殊字符:四个特殊字符位置是第5 8 11 14，第5 8 14是根据平台确定的，且各个节目都一样。第11位在h5上是根据节目ID第1位(从0开始,android是第6位)数字为下标的某字符串的值
 * 在android，标清画质还有区分，第5位字符需要修改，其他不变
 * @param {string} puData - 服务器返回的那个东东
 * @param {string} programId - 节目ID
 * @param {string} clientType - 平台类型 h5 android
 * @param {string} rateType - 清晰度 2:标清 3:高清 4:蓝光
 * @returns {string} - ddCalcu
 */
function getddCalcu(puData, programId, clientType, rateType) {

  if (puData == null || puData == undefined) {
    return ""
  }

  if (programId == null || programId == undefined) {
    return ""
  }

  if (clientType != "android" && clientType != "h5") {
    return ""
  }

  if (rateType == null || rateType == undefined) {
    return ""
  }
  let keys = list[clientType].keys
  let words = list[clientType].words
  const thirdReplaceIndex = list[clientType].thirdReplaceIndex
  // android平台标清
  if (clientType == "android" && rateType == "2") {
    words[0] = "v"
  }
  puData = puData.split("");
  keys = keys.split("")
  const puDataLength = puData.length
  programId = programId.split("")
  let ddCalcu = []
  for (let i = 0; i < puDataLength / 2; i++) {

    ddCalcu.push(puData[puDataLength - i - 1])
    ddCalcu.push(puData[i])
    switch (i) {
      case 1:
        ddCalcu.push(words[i - 1])
        break;
      case 2:
        ddCalcu.push(words[i - 1])
        break;
      case 3:
        ddCalcu.push(keys[programId[thirdReplaceIndex]])
        break;
      case 4:
        ddCalcu.push(words[i - 1])
        break;
    }
  }
  return ddCalcu.join("")
}

/**
 * 加密链接
 * @param {string} puDataURL - 加密前链接
 * @param {string} programId - 节目ID
 * @param {string} clientType - 客户端类型 h5 android
 * @param {string} rateType - 清晰度 2:标清 3:高清 4:蓝光
 * @returns {string} - 加密链接
 */
function getddCalcuURL(puDataURL, programId, clientType, rateType) {

  if (puDataURL == null || puDataURL == undefined) {
    return ""
  }

  if (programId == null || programId == undefined) {
    return ""
  }

  if (clientType != "android" && clientType != "h5") {
    return ""
  }

  if (rateType == null || rateType == undefined) {
    return ""
  }

  const puData = puDataURL.split("&puData=")[1]
  const ddCalcu = getddCalcu(puData, programId, clientType, rateType)
  const suffix = list[clientType].suffix

  return `${puDataURL}&ddCalcu=${ddCalcu}${suffix}`
}


/**
 * 旧版720p ddcalcu
 * @param {string} puData - 服务器返回的那个东东
 * @param {string} programId - 节目ID
 * @returns {string} - ddCalcu
 */
function getddCalcu720p(puData, programId) {

  if (puData == null || puData == undefined) {
    return ""
  }

  if (programId == null || programId == undefined) {
    return ""
  }

  const words = ["e","2","","0"]
  const thirdReplaceIndex = 2

  puData = puData.split("");
  const keys = "0123456789".split("")
  const puDataLength = puData.length

  programId = programId.split("")
  let ddCalcu = []
  for (let i = 0; i < puDataLength / 2; i++) {

    ddCalcu.push(puData[puDataLength - i - 1])
    ddCalcu.push(puData[i])
    switch (i) {
      case 1:
        ddCalcu.push(words[i - 1])
        break;
      case 2:
        ddCalcu.push(words[i - 1])
        break;
      case 3:
        ddCalcu.push(keys[programId[thirdReplaceIndex]])
        break;
      case 4:
        ddCalcu.push(words[i - 1])
        break;
    }
  }
  return ddCalcu.join("")
}

/**
 * 旧版720p加密链接
 * @param {string} puDataURL - 加密前链接
 * @param {string} programId - 节目ID
 * @returns {string} - 加密链接
 */
function getddCalcuURL720p(puDataURL, programId) {

  if (puDataURL == null || puDataURL == undefined) {
    return ""
  }

  if (programId == null || programId == undefined) {
    return ""
  }

  const puData = puDataURL.split("&puData=")[1]
  const ddCalcu = getddCalcu720p(puData, programId)

  return `${puDataURL}&ddCalcu=${ddCalcu}`
}

export { initWasm, getEncryptURL, getddCalcuURL, getddCalcuURL720p }
