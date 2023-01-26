cd C:\Users\Dave.Mauney\PycharmProjects\Automation\Internal\SiteMapper
py site_mapper.py > log.txt
cd C:\Users\Dave.Mauney\PycharmProjects\Automation\docs >> log.txt
copy *.html C:\Users\Dave.Mauney\PycharmProjects\Automation\Internal\SiteMapper >> log.txt
git status >> log.txt
git commit -a -m "SiteMapper Scheduled Run" >> log.txt
git push origin HEAD:main >> log.txt