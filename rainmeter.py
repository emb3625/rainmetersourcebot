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
USERNAME=USERNAME
PASSWORD=PASSWORD
CLIENT_ID=CLIENT_ID
CLIENT_SECRET=CLIENT_SECRET

r = praw.Reddit(user_agent="/r/rainmeter source enforcer by /u/Pandemic21",
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                username=USERNAME,
                password=PASSWORD)
GRACE_PERIOD=60*60 # 1 hour in seconds
END_CHECKING_PERIOD=60*60*6 # 6 hours in seconds
COMMENT_TEXT=("Thank you for [your submission]({url}). Your post has been temporarily removed because it looks like your submission does not comply with rule 1 of the posting rules.\n\n"
              ">**Provide all download links** for any skins, wallpapers, etc. in your post.\n\n"
              "Please reply to your submission with the download links and then wait ~10 minutes for the automated process to approve the post. "
              "If by then your post is not approved, or if you believe it was falsly flagged, reply to this conversation to notify the moderators."
              "\n\n***\n\n^I ^am ^a ^bot, ^created ^by [^Pandemic21](https://reddit.com/u/pandemic21) ^and ^also ^modified ^by "
              "[^NighthawkSLO](https://reddit.com/u/NighthawkSLO)^. ^I ^help ^keep ^the ^peace ^here. "
              "[^About](https://emb3625.github.io/rainmetersourcebot) ^| [^Inquiries](https://www.reddit.com/message/compose?to=%2Fr%2Frainmeter&subject=rainmetersourcebot) ^| "
              "[^Changelog](https://github.com/emb3625/rainmetersourcebot/releases/) ^| [^Source ^Code](https://github.com/emb3625/rainmetersourcebot)")
APPROVED_TEXT=("Found the sources and approved the post.\n\n***\n\n"
               "^I ^am ^a ^bot, ^created ^by [^Pandemic21](https://reddit.com/u/pandemic21) ^and ^also ^modified ^by "
               "[^NighthawkSLO](https://reddit.com/u/NighthawkSLO)^. ^I ^help ^keep ^the ^peace ^here. "
               "[^About](https://emb3625.github.io/rainmetersourcebot) ^| [^Inquiries](https://www.reddit.com/message/compose?to=%2Fr%2Frainmeter&subject=rainmetersourcebot) ^| "
               "[^Changelog](https://github.com/emb3625/rainmetersourcebot/releases/) ^| [^Source ^Code](https://github.com/emb3625/rainmetersourcebot)")
sub = r.subreddit("rainmeter")
d = {}

while 1:
	#search for new submissions
	posts = sub.new(limit=10)
	for post in posts:
		if post.is_self:
			gen_log(post.id + " is a self-post")
			continue
		if post.approved_by is not None:
			gen_log(post.id + " is approved by %s" % post.approved_by)
			continue
		if post.link_flair_text is None or search("(?i)Showcase|First|OC(?! )|SotM|To Be", post.link_flair_text) is None:
			#this searches for unflaired posts and Showcase, First Attempt, OC, SotM and To Be Tagged... flairs, if
			#it does not find the correct strings they have a flair where the rule doesn't apply
			gen_log(post.id + " has the flair %s" % post.link_flair_text)
			continue
		if get_entry_exists(post.id):
			gen_log(post.id + " has already been added")
			continue
		gen_log("Adding " + post.id)
		d[post.id] = {"time": int(post.created_utc) + GRACE_PERIOD, "modmail": None}

	#check old submissions
	t = time.time()

	for key in d.keys():
		if float(d[key]["time"]) > t:
			gen_log(str(key) + " has " + str(int((d[key]["time"])-t)/60) + " minutes left")
			continue
		if float(d[key]["time"] + END_CHECKING_PERIOD) < t:
			gen_log(str(key) + " has been without links for too long, stopped checking")
			#delete dictionary entry
			d.pop(key)
			continue

		gen_log("Checking " + str(key) + "...")

		op_has_replied = False
		s = r.submission(id=key)
		op = str(s.author)
		comments = s.comments

		for comment in comments:
			if op == str(comment.author):
				gen_log("OP replied, comment.id = " + comment.id)
				op_has_replied = True
				break
		if op_has_replied:
			if d[key]["modmail"] is not None:
				#approve post
				s.mod.approve()
				d[key]["modmail"].reply(APPROVED_TEXT)
				d[key]["modmail"].archive()
			#delete dictionary key
			d.pop(key)
			continue
		gen_log("OP hasn't replied, messaging")
		d[key]["modmail"] = sub.modmail.create("Your submission has been removed", COMMENT_TEXT.format(url=s.shortlink), s.author)
		s.mod.remove()

	time.sleep(60*5) # 5 miutes in seconds
