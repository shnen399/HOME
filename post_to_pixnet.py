def post_to_pixnet(email, password, article, keywords):
    username = email.split("@")[0]
    fake_post_id = "123456789"
    blog_link = f"https://{username}.pixnet.net/blog/post/{fake_post_id}"
    return True, blog_link
