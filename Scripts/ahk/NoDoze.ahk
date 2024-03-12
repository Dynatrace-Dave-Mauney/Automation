#Persistent
SetTimer, CheckIdle, 60000    ; 60 sec / 1 min
Return

CheckIdle:
If (A_TimeIdle > 60000)
{
    Send {RShift}
}
Return