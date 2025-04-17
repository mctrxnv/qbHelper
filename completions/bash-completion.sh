_qbt_controller_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    if [[ ${prev} == "qbt-controller" ]]; then
        opts="list add delete pause resume recheck --help"
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    elif [[ ${prev} == @(delete|pause|resume|recheck) ]]; then
        local torrents
        torrents=$(qbt-controller --complete ${prev} 2>/dev/null)
        COMPREPLY=( $(compgen -W "${torrents}" -- ${cur}) )
    fi
}

complete -F _qbt_controller_completion qbt-controller
