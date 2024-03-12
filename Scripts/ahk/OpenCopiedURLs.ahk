; https://superuser.com/questions/469380/how-to-open-multiple-links-url-using-autohotkey
; CTRL-ALT-C
; Fails for long URLs!
;
; The "Open Multiple URLs" Chrome extension works well for this use case!
;
^!c::
  oCB := ClipboardAll
  Send ^c
  Loop,parse,clipboard,`n,`r
  {
    Run %A_LoopField%
  }
  ClipBoard := %oCB%