import praw
import time
from re import search


def get_entry_exists(submission_id):
	for key in d.keys():
		if key == submission_id:
			return True
	return False


def gen_log(data):
	datetime =  str(time.strftime("%Y/%m/%d")) + " " + str(time.strftime("%H:%M:%S"))
	print datetime + ": " + data


### MAIN #############################################
r = praw.Reddit("/r/rainmeter source enforcer by /u/Pandemic21")
USERNAME='rainmetersourcebot'
PASSWORD='<password>'
GRACE_PERIOD=60*60*3 # 3 hours in seconds 
COMMENT_TEXT="Thank you for your submission. Your post has been temporarily removed because it looks like your submission does not comply with Rule B1.\n\n>With the exception of OC WIP posts, **provide download links** to skins, wallpapers, and visualizers shown in any content submission **within three hours** of posting.\n\nPlease reply to your submission with the download links and then [click here to send the subreddit a modmail](https://www.reddit.com/message/compose?to=%2Fr%2FRainmeter&subject=Please+approve+my+post&message=I+added+download+links+to+my+post.+Can+you+please+approve+it?+Thank+you!+**DOWNLOAD+LINK+HERE**) so your post can be approved. Thank you. \n\n***\n\n^I ^am ^a ^bot, ^created ^by [^Pandemic21](https://reddit.com/u/pandemic21) ^and ^also ^modified ^by [^NighthawkSLO](https://reddit.com/u/NighthawkSLO)^. [^About](https://emb3625.github.io/rainmetersourcebot) ^| [^Inquiries](https://www.reddit.com/message/compose?to=%2Fr%2Frainmeter&subject=rainmetersourcebot) ^| [^Changelog](https://github.com/emb3625/rainmetersourcebot/releases/) ^| [^Source ^Code](https://github.com/emb3625/rainmetersourcebot)"
sub = r.get_subreddit("rainmeter")
d = {}

r.login(USERNAME,PASSWORD,disable_warning=True)

while 1:
    #search for new submissions
    posts = sub.get_new(limit=10)
    for post in posts:
        if post.is_self:
            gen_log(post.id + " is a self-post")
            continue
        if post.approved_by is not None:
            gen_log(post.id + " is approved by %s" % post.approved_by)
            continue
        if search("(?i)Showcase|First|OC(?! )|SotM|To Be", post.link_flair_text) is None:
            #this searches for Showcase, First Attempt, OC, SotM and To Be Tagged... flairs, if
            #it does not find the correct strings they have a flair where the rule doesn't apply
            gen_log(post.id + " has the flair %s" % post.link_flair_text)
            continue
        if get_entry_exists(post.id):
            gen_log(post.id + " has already been added")
            continue
        gen_log("Adding " + post.id)
        d[post.id] = int(post.created_utc) + GRACE_PERIOD

	#check old submissions
	t = time.time()

	for key in d.keys():
		if float(d[key]) > t:
			gen_log(str(key) + " has " + str(int((d[key])-t)/60) + " minutes left")
			continue

		gen_log("Checking " + str(key) + "...")
		
		op_has_replied = False
		s = r.get_submission(submission_id=key)
		op = str(s.author)
		comments = s.comments

		for comment in comments:
			if op == str(comment.author):
				gen_log("OP replied, comment.id = " + comment.id)
				op_has_replied = True
		if op_has_replied:
			#delete dictionary key
			d.pop(key)
			continue
		gen_log("OP hasn't replied, adding comment")
		praw.objects.Moderatable.distinguish(s.add_comment(COMMENT_TEXT))
		s.remove()
		#delete dictionary entry
		d.pop(key)

	time.sleep(60*10) # 10 miutes in seconds
