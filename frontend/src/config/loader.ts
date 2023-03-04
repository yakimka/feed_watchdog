/*
 * Get config value  with precedence:
 * - check `process.env`
 * - check current web page meta tags
 * @param {string} key Configuration key name
 */
function getConfigValue (key: string) {
  let value = null
  if (process.env && process.env[`${key}`] !== undefined) {
    // get env var value
    value = process.env[`${key}`]
  } else {
    // get value from meta tag
    return getMetaValue(key)
  }
  return value
}

/*
 * Get value from HTML meta tag
 */
function getMetaValue (key: string) {
  let value = null
  const node = document.querySelector(`meta[property=${key}]`)
  if (node instanceof HTMLMetaElement) {
    value = node.content
  }
  return value
}

export default { getConfigValue, getMetaValue }
