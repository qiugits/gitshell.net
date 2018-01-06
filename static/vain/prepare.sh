function prepare () {
    # https://askubuntu.com/questions/271776/how-to-resize-an-image-through-the-terminal
    # https://qiita.com/sowd/items/832594dd22d99aebc8a2
    mkdir "${1}-${2}"
    for n in $1/*.png; do
        newfname=$(echo "${n}" | sed "s/${1}/${1}-${2}/g")
        convert -resize "${2}x${2}" "${n}" "${newfname}"
    done
    rm "sprite/${1}-${2}.css"
    glue "${1}-${2}" sprite -p=1 --css-template sprite/css-template.css
}
prepare items 64
prepare hero 288
prepare hero 32

# function e () {
#     echo "${1}-${2}"
# }
# e items 64
