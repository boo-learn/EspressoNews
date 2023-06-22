from sqlalchemy.orm import Session

from shared.models import Post


# TODO
def get_posts_without_summary(limit: int = 50):
    pass
    # return db.query(Post).filter(Post.summary.is_(None)).limit(limit).all()


# TODO
def update_post_summary(post_id: int, summary: str):
    pass
    # post = db.query(Post).filter(Post.post_id == post_id).one()
    # post.summary = summary
    # db.commit()


# TODO
def get_active_gpt_accounts():
    pass
    # session = Session()
    # active_accounts = session.query(GPTAccount).filter(GPTAccount.is_active == True).all()
    # session.close()
    # return active_accounts
