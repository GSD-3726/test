import fs from "fs"
import { dataList, delay, getUrlInfo } from "./utils/fetchList.js"
import { getEncryptURL, initWasm } from "./utils/ddCalcuURL.js"

async function fetchURLByWasm() {

  // 必须绝对路径
  let path = process.cwd() + '/interface.txt'
  // 文件不存在则创建
  if (!fs.existsSync(path)) {
    fs.writeFile(path, "", error => {
      if (error) {
        throw new Error("文件创建失败")
      }
      console.log("文件创建成功")
    })
  }
  // 等待文件创建
  await delay(500)

  // 备份文件
  fs.copyFile(path, path + ".bak", error => {
    if (error) {
      throw error
    }
    console.log("文件备份成功")
  })

  // 等待文件备份
  await delay(500)
  fs.writeFile(path, "", error => {
    if (error) {
      throw new Error("文件清除失败")
    }
    console.log("文件清除成功")
  })
  // 所有数据
  let datas = await dataList()
  // const datas = channelName
  // 获取加密方法
  const exports = await initWasm("https://m.miguvideo.com/mgs/player/prd/v_20250506111629_ddc2c612/dist/pickproof1000.wasm")
  // 写入分类
  for (let i = 0; i < datas.length; i++) {
    console.log("正在写入分类###:" + datas[i].name)
    // 写入分类数据
    fs.appendFile(path, datas[i].name + ",#genre#\n", error => {
      if (error) {
        throw new Error("写入失败")
      }
    })

    let data = datas[i].dataList
    // 写入分类中的节目
    for (let j = 0; j < data.length; j++) {
      console.log("正在准备节目")
      let link
      // console.log(data[j].pID)
      // 获取播放链接
      let url = await getUrlInfo(data[j].pID)
      if (url == "") {
        console.log(data[j].name + "：节目调整，暂不提供服务")
        continue
      }
      // 加密链接
      link = getEncryptURL(exports, url)

      if (!link) {
        continue
      }
      console.log("正在写入节目:" + data[j].name)
      // 写入分类数据
      fs.appendFile(path, data[j].name + "," + link + "\n", error => {
        if (error) {
          throw new Error("写入失败")
        }
      })
    }
  }
}

fetchURLByWasm()
