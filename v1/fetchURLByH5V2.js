import { dataList, getUrlInfo } from "./utils/fetchList.js"
import { getddCalcuURL } from "./utils/ddCalcuURL.js"
import { appendFile, writeFile } from "./utils/fileUtil.js"
import { updatePlaybackData } from "./utils/playback.js"

// h5端修改频繁
async function fetchURLByH5() {

  const date = new Date()
  const start = date.getTime()

  // aptv 必须绝对路径
  const path = process.cwd() + '/interface.txt'
  // 创建写入空内容
  writeFile(path, "")

  // 所有数据
  const datas = await dataList()

  const hours = date.getHours()
  let playbackFile = ""
  // 0点
  if (!hours) {
    playbackFile = process.cwd() + '/playback.xml'
    writeFile(playbackFile,
      `<?xml version="1.0" encoding="UTF-8"?>\n` +
      `<tv generator-info-name="Tak" generator-info-url="https://gitee.com/dream-deve/migu_video/raw/main/playback.xml">\n`)
  }
  // 写入开头
  appendFile(path, `#EXTM3U x-tvg-url="https://gitee.com/dream-deve/migu_video/raw/main/playback.xml" catchup="append" catchup-source="&playbackbegin=\${(b)yyyyMMddHHmmss}&playbackend=\${(e)yyyyMMddHHmmss}"\n`)

  // 写入分类
  for (let i = 0; i < datas.length; i++) {
    console.log(`分类###:${datas[i].name}`)

    const data = datas[i].dataList

    // 遍历节目
    for (let j = 0; j < data.length; j++) {

      if (!hours) {
        const res = await updatePlaybackData(data[j], playbackFile)
        if (!res) {
          console.log(`playback.xml更新失败`)
        }
      }
      // 获取播放链接
      const url = await getUrlInfo(data[j].pID)
      if (url == "") {
        console.log(`${data[j].name}：节目调整，暂不提供服务`)
        continue
      }
      // 加密链接
      // const link = getEncryptURL(exports, url)
      const link = getddCalcuURL(url, data[j].pID, "h5", "999")

      console.log(`正在写入节目:${data[j].name}`)

      // 写入节目
      appendFile(path, `#EXTINF:-1 svg-id="${data[j].name}" svg-name="${data[j].name}" tvg-logo="${data[j].pics.highResolutionH}" group-title="${datas[i].name}",${data[j].name}\n${link}\n`)
    }
  }
  if (!hours) {
    appendFile(playbackFile, `</tv>\n`)
  }
  const end = Date.now()
  console.log(`本次耗时:${(end - start) / 1000}秒`)
}

fetchURLByH5()
