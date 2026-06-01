require ["vnd.dovecot.pipe", "copy", "environment", "imapsieve", "variables" ];

if environment :matches "imap.mailbox" "*" {
  set "mailbox" "${1}";
}

if string :matches "${mailbox}" ["*/Trash", "Trash"] {
  stop;
}

pipe :copy "rspamd-learn.sh" [ "ham" ];
