cd C:\src\github\Automation\Internal\SiteMapper
py site_mapper.py > C:\src\github\Automation\Internal\SiteMapper\log.txt
cd C:\src\github\Automation\docs >> C:\src\github\Automation\Internal\SiteMapper\log.txt
copy *.html C:\src\github\Automation\Internal\SiteMapper >> C:\src\github\Automation\Internal\SiteMapper\log.txt
pause
git status >> C:\src\github\Automation\Internal\SiteMapper\log.txt
pause
git commit -a -m "SiteMapper Scheduled Run" >> C:\src\github\Automation\Internal\SiteMapper\log.txt
pause
git push origin HEAD:main >> C:\src\github\Automation\Internal\SiteMapper\log.txt
pause