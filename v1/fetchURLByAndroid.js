import fs from "fs"
import { delay } from "./utils/fetchList.js"
import { initWasm } from "./utils/ddCalcuURL.js"
import getAndroidVideoURL from "./utils/androidURL.js"
import { channelName } from "./utils/datas.js"
import refreshToken from "./utils/refreshToken.js"

async function fetchURLByAndroid() {

  const userId = process.env.USERID
  const token = process.env.MIGU_TOKEN

  const start = Date.now()
  // 必须绝对路径
  const path = process.cwd() + '/interface.txt'
  // 文件不存在则创建
  if (!fs.existsSync(path)) {
    fs.writeFile(path, "", error => {
      if (error) {
        throw new Error("文件创建失败")
      }
      console.log("文件创建成功")
    })
  }

  // aptv 必须绝对路径
  const aptvPath = process.cwd() + '/interface-aptv.txt'
  // 文件不存在则创建
  if (!fs.existsSync(aptvPath)) {
    fs.writeFile(aptvPath, "", error => {
      if (error) {
        throw new Error("文件创建失败")
      }
      console.log("文件创建成功")
    })
  }
  // 备份文件
  // fs.copyFile(path, path + ".bak", error => {
  //   if (error) {
  //     throw error
  //   }
  //   console.log("文件备份成功")
  // })

  // await delay(100)
  // 清除文件内容
  fs.writeFile(path, "", error => {
    if (error) {
      throw new Error("文件清除失败")
    }
    console.log("文件清除成功")
  })

  // 清除aptv文件内容
  fs.writeFile(aptvPath, "", error => {
    if (error) {
      throw new Error("aptv文件清除失败")
    }
    console.log("aptv文件清除成功")
  })

  const rateDesc = ["", "", "标清", "高清", "蓝光"]

  // 刷新token 0点刷新token
  if (!new Date(start).getHours()) {
    await refreshToken(userId, token) ? console.log("token刷新成功") : console.log("token刷新失败")
  }
  // 获取数据
  // const datas = await dataList()
  const datas = channelName
  // 获取加密方法
  const exports = await initWasm("https://m.miguvideo.com/mgs/player/prd/v_20250506111629_ddc2c612/dist/pickproof1000.wasm")
  // console.log("{")

  // aptv写入开头
  fs.appendFile(aptvPath, `#EXTM3U\n`, error => {
    if (error) {
      throw new Error("写入失败")
    }
  })

  // 分类列表
  for (let i = 0; i < datas.length; i++) {
    console.log(`正在写入分类###:${datas[i].cateName}`)
    // 写入分类数据
    fs.appendFile(path, `${datas[i].cateName},#genre#\n`, error => {
      if (error) {
        throw new Error("写入失败")
      }
    })

    const data = datas[i].data
    // console.log(`"${datas[i].name}": {`)
    // 写入分类中的各个频道
    for (let j = 0; j < data.length; j++) {
      // console.log(`"${data[j].name}": ${data[j].pID},`)
      // console.log("正在准备节目")
      let rateType = 4
      if (userId == null || userId == undefined || token == null || token == undefined) {
        rateType = 2
      }
      // 写入分辨率
      for (let z = 0; z < 3; z++) {
        // console.log(data[j].pID)
        const resObj = await getAndroidVideoURL(userId, token, exports, data[j].pid, rateType)
        if (resObj.url == "") {
          console.log(`${data[j].name}：节目调整，暂不提供服务`)
          break
        }
        console.log(`正在写入节目:${data[j].name}$${rateDesc[resObj.rateType]}`)
        // 写入分类数据
        fs.appendFile(path, `${data[j].name},${resObj.url}$${rateDesc[resObj.rateType]}\n`, error => {
          if (error) {
            throw new Error("写入失败")
          }
        })
        // 写入aptv分类数据
        fs.appendFile(aptvPath, `#EXTINF:-1 svg-name="${data[j].name}" group-title="${datas[i].cateName}",${data[j].name}\n${resObj.url}\n`, error => {
          if (error) {
            throw new Error("写入失败")
          }
        })
        // 依次降低画质
        rateType = resObj.rateType - 1
        // 返回为标清就结束
        if (resObj.rateType == 2) {
          break
        }
      }
    }
    await delay(100)
    // console.log("},")
  }
  // console.log("}")
  const end = Date.now()
  console.log(`本次耗时:${(end - start) / 1000}秒`)
}

fetchURLByAndroid()
