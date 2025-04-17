function __qbt_complete_torrents
    qbt-controller --complete $argv[1] 2>/dev/null | while read -l hash name
        echo -e "$hash\t$name"
    end
end

complete -c qbt-controller -n __fish_use_subcommand -xa "list add delete pause resume recheck" -d "qBittorrent controller"
complete -c qbt-controller -n "__fish_seen_subcommand_from delete" -xa "(__qbt_complete_torrents delete)"
complete -c qbt-controller -n "__fish_seen_subcommand_from pause" -xa "(__qbt_complete_torrents pause)"
complete -c qbt-controller -n "__fish_seen_subcommand_from resume" -xa "(__qbt_complete_torrents resume)"
complete -c qbt-controller -n "__fish_seen_subcommand_from recheck" -xa "(__qbt_complete_torrents recheck)"
