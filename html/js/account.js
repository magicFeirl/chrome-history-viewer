export const liveCheck = (emailList) => {
    const emailListStr = emailList.join('\n\n')
    console.info(emailListStr)

    navigator.clipboard.writeText(emailListStr).then(() => {
        window.open('https://colab.research.google.com/drive/1O2gn4gCyGGFmo1aL97rB8L7ZozmGw1qL', '_blank')
    }).catch((e) => {
        alert('写入剪贴板失败，请手动在控制台复制邮箱')
        console.error(e)
    })
}