import crypto from 'crypto'
import CryptoJS from 'crypto-js';

const KEY_AES = "MQDUjI19MGe3BhaqTlpc9g==";
const IV = "abcdefghijklmnop";

const RSA_PRIVATE_KEY_PKCS8 = "MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAOhvWsrglBpQGpjB\r8okxLUCaaiKKOytn9EtvytB5tKDchmgkSaXpreWcDy/9imsuOiVCSdBr6hHjrTN7\rQKkA4/QYS8ptiFv1ap61PiAyRFDI1b8wp2haJ6HF1rDShG2XdfWIhLk4Hj6efVZA\rSfa3taM7C8NseWoWh05Cp26g4hXZAgMBAAECgYBzqZXghsisH1hc04ZBRrth/nT6\rIxc2jlA+ia6+9xEvSw2HHSeY7COgsnvMQbpzg1lj2QyqLkkYBdfWWmrerpa/mb7j\rm6w95YKs5Ndii8NhFWvC0eGK8Ygt02DeLohmkQu3B+Yq8JszjB7tQJRR2kdG6cPt\rKp99ZTyyPom/9uD+AQJBAPxCwajHAkCuH4+aKdZhH6n7oDAxZoMH/mihDRxHZJof\rnT+K662QCCIx0kVCl64s/wZ4YMYbP8/PWDvLMNNWC7ECQQDr4V23KRT9fAPAN8vB\rq2NqjLAmEx+tVnd4maJ16Xjy5Q4PSRiAXYLSr9uGtneSPP2fd/tja0IyawlP5UPL\rl76pAkAeXqMWAK+CvfPKxBKZXqQDQOnuI2RmDgZQ7mK3rtirvXae+ciZ4qc4Bqt7\r7yJ3s68YRlHQR+OMzzeeKz47kzZhAkAPteH1ChJw06q4Sb8TdiPX++jbkFiCxgiN\rCsaMTfGVU/Y8xGSSYCgPelEHxu1t2wwVa/tdYs505zYmkSGT1NaJAkBCS5hymXsA\rB92Fx8eGW5WpLfnpvxl8nOcP+eNXobi8Sc6q1FmoHi8snbcmBhidcDdcieKn+DbX\rGG3BQE/OCOkM\r";

// MD5标准加密
function getStringMD5(str) {
  // 创建 MD5 哈希对象
  const md5 = crypto.createHash("md5");
  // 更新数据（默认 UTF-8 编码）
  md5.update(str);
  // 生成十六进制哈希值并转为小写
  return md5.digest("hex").toLowerCase();
}

/**
 * base64加密
 */
function Base64encrypt(str) {
  // create a buffer
  const buff = Buffer.from(str, 'utf-8');
  // encode buffer as Base64
  return buff.toString('base64')
}

/**
 * base64解密
 */
function Base64decrypt(str) {
  // create a buffer
  const buff = Buffer.from(str, 'base64');
  // encode buffer as Base64
  return buff.toString('utf-8')
}

// AES 解密方法
function AESdecrypt(encryptedText, base64Key) {
  // 解码 Base64 密钥和密文
  const keyBytes = CryptoJS.enc.Base64.parse(base64Key);
  const encryptedBytes = CryptoJS.enc.Base64.parse(encryptedText);

  // 处理 IV
  const iv = CryptoJS.enc.Utf8.parse(IV);

  // 配置解密参数
  const decryptOptions = {
    iv: iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  };

  // 执行 AES 解密
  const decrypted = CryptoJS.AES.decrypt(
    { ciphertext: encryptedBytes },
    keyBytes,
    decryptOptions
  );

  // 将解密结果转为 UTF-8 字符串
  return decrypted.toString(CryptoJS.enc.Utf8);
}

// AES 加密方法
function AESencrypt(str, base64Key) {
  // 解码 Base64 密钥
  const keyBytes = CryptoJS.enc.Base64.parse(base64Key);

  // 处理 IV 和明文
  const iv = CryptoJS.enc.Utf8.parse(IV);
  const plainBytes = CryptoJS.enc.Utf8.parse(str);

  // 配置加密参数
  const encryptOptions = {
    iv: iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  };

  // 执行 AES 加密
  const encrypted = CryptoJS.AES.encrypt(
    plainBytes,
    keyBytes,
    encryptOptions
  );

  // 返回 Base64 编码的密文
  return encrypted.ciphertext.toString(CryptoJS.enc.Base64);
}

/**
 *RSA 加密
 */
function RSAencrypt(str) {
  // 处理密钥：移除 \r 并解码 Base64
  const keyBytes = Buffer.from(RSA_PRIVATE_KEY_PKCS8.replace(/\r/g, ''), 'base64');

  // 创建私钥对象
  const privateKey = crypto.createPrivateKey({
    key: keyBytes,
    format: 'der',
    type: 'pkcs8'
  });

  // 使用私钥加密
  const encrypted = crypto.privateEncrypt(
    { key: privateKey, padding: crypto.constants.RSA_PKCS1_PADDING },
    Buffer.from(str)
  );

  return encrypted.toString('base64');
}

export { getStringMD5, KEY_AES, AESdecrypt, AESencrypt, Base64decrypt, Base64encrypt, RSAencrypt }
