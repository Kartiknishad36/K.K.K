# Feature Pack (`bot/plugins/features`)

Only **new** commands — duplicates with core plugins removed.

## Kept here
| Command | File |
|---------|------|
| `.spam` `.typing` `.typing24` | purge_spam_typing.py |
| `.kang` `.sticker` | stickers_extra.py |
| `.truth` `.dare` `.riddle` `.quiz` | translate_games.py |
| `.af` `.afset` `.fwd` `.fcomment` | forward_comment.py |
| `.giveaway` `.bdayadd` `.bdays` | giveaway_bday.py |
| `.protect` `.cctv` | protect_cctv.py |
| `.meme` `.fakeloc` | meme_media.py |
| `.aidost` `.biz` `.bizadd` | ai_chat_business.py |
| `.gm` `.gmnow` `.search` | morning_search.py |
| `.movie` | movie_filter.py |
| `.backup` `.chatlock` `.autodelchat` | backup_extra.py |
| `.arphoto` `.vtt` | voice_photo_extra.py |
| `.fhelp` | features_help.py |

## Not duplicated (already in core)
| Command | Core file |
|---------|-----------|
| `.purge` | admin.py |
| `.tr` / `.translate` | tools.py |
| `.filter` / `.filters` | filters.py |
| `.alive` `.ping` `.help` | main / start |
| `.afk` | afk.py |
| `.tagall` | tagall.py |
| `.auto` | self_ai.py |
| `.login` | login.py |
| `.deleted` | deleted_logger.py |

## Skipped (safety)
Fake Pay, OTP forward, Member chori, Fake Blue Tick, WhatsApp bridge, profile-view spy.
