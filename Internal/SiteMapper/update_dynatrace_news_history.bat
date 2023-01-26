cd C:\src\github\Automation\Internal\SiteMapper
git fetch --all > C:\src\github\Automation\Internal\SiteMapper\log.txt
git reset --hard origin/main >> C:\src\github\Automation\Internal\SiteMapper\log.txt
py site_mapper.py >> C:\src\github\Automation\Internal\SiteMapper\log.txt
cd C:\src\github\Automation\docs >> C:\src\github\Automation\Internal\SiteMapper\log.txt
copy dynatrace*.html C:\src\github\Automation\Internal\SiteMapper >> C:\src\github\Automation\Internal\SiteMapper\log.txt
git status >> C:\src\github\Automation\Internal\SiteMapper\log.txt
git commit -a -m "SiteMapper Scheduled Run" >> C:\src\github\Automation\Internal\SiteMapper\log.txt
git push origin HEAD:main >> C:\src\github\Automation\Internal\SiteMapper\log.txt
