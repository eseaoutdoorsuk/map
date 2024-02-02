/**
 * Clean phone number
 * @param {number} num phone number
 * @return cleaned number
 * @customfunction
*/
function cleanNumber(num) {
  let clean = num.toString().replace(/\D/g,'')
  if (clean == "") {
    return ""
  }
  
  if (clean.startsWith("07")){
    return "447" + clean.slice(2)
  }

  if (clean.startsWith("4407")){
    return "447" + clean.slice(4)
  }
  
  return clean
}

/**
 * Build WA URL
 * @param {number} num phone number
 *  @param {string} text text
 *  @param {string} name name
 * @return WA URL
 * @customfunction
*/
function buildWAURL(num, text, name){
  if (num == "") {
    return ""
  }
  
  totalText = `Hi ${name.trim().split(" ")[0]}! ${text}`

  return `https://wa.me/${num}?text=${encodeURIComponent(totalText)}`
}