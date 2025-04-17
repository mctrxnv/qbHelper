#compdef qbt-controller

_qbt_controller() {
    local state
    _arguments \
        '1: :->command' \
        '*: :->args'
    
    case $state in
        command)
            local -a commands
            commands=(
                'list:Show torrent list'
                'add:Add new torrent'
                'delete:Delete torrents'
                'pause:Pause torrents'
                'resume:Resume torrents'
                'recheck:Recheck torrents'
            )
            _describe 'command' commands
            ;;
        args)
            case $words[1] in
                delete|pause|resume|recheck)
                    local -a torrents
                    torrents=($(qbt-controller --complete $words[1] 2>/dev/null))
                    _arguments '*:torrent:($torrents)'
                    ;;
            esac
            ;;
    esac
}

_qbt_controller "$@"
