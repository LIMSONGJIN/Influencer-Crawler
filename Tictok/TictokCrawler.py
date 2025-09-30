import requests
import random
from TikTokApi import TikTokApi
from openpyxl import Workbook
import asyncio

def get_random_proxy():
    """
    무료 프록시 API에서 랜덤으로 하나 뽑기
    """
    try:
        resp = requests.get("https://www.proxy-list.download/api/v1/get?type=http", timeout=5)
        proxies = [line.strip() for line in resp.text.splitlines() if line.strip()]
        if proxies:
            return random.choice(proxies)
        return None
    except Exception as e:
        print(f"프록시 불러오기 실패: {e}")
        return None

def make_proxy_dict(proxy_str):
    return {"server": f"http://{proxy_str}"}

class TikTokCrawler:
    def __init__(self):
        self.api = TikTokApi()
        self.last_proxy = None

    async def create_sessions(self, num_sessions=1, use_proxy=True):
        proxies = []
        if use_proxy:
            proxy_str = get_random_proxy()
            self.last_proxy = proxy_str
            if proxy_str:
                proxies = [make_proxy_dict(proxy_str) for _ in range(num_sessions)]
                print(f"랜덤 프록시 사용: {proxy_str}")
            else:
                print("프록시를 불러오지 못해 프록시 없이 시도합니다.")
        await self.api.create_sessions(
            num_sessions=num_sessions,
            headless=False,
            browser="webkit",
            proxies=proxies if proxies else None
        )
        print(f"세션 {num_sessions}개 생성 완료 (proxy: {self.last_proxy})")

    async def crawl_hashtag(self, hashtag: str, limit: int = 50):
        hashtag_obj = self.api.hashtag(name=hashtag)
        videos = []
        count = 0
        async for video in hashtag_obj.videos(count=limit):
            info = self.extract_video_info(video)
            if info:
                videos.append(info)
            count += 1
            if count >= limit:
                break
        return videos

    async def crawl_user(self, username: str, limit: int = 50):
        user_obj = self.api.user(username=username)
        videos = []
        count = 0
        async for video in user_obj.videos(count=limit):
            info = self.extract_video_info(video)
            if info:
                videos.append(info)
            count += 1
            if count >= limit:
                break
        return videos

    def extract_video_info(self, video):
        try:
            return {
                'video_id': video.id,
                'desc': video.desc,
                'create_time': video.create_time,
                'author_name': video.author.nickname,
                'author_id': video.author.unique_id,
                'follower_count': getattr(video.author.stats, 'follower_count', 0),
                'digg_count': video.stats.digg_count,
                'comment_count': video.stats.comment_count,
                'share_count': video.stats.share_count,
                'play_count': video.stats.play_count,
                'video_url': video.video.play_addr,
                'cover_url': video.video.cover,
                'music_title': getattr(video.music, 'title', ''),
                'hashtags': [tag.name for tag in getattr(video, 'challenges', [])],
            }
        except Exception as e:
            print(f"데이터 파싱 실패: {e}")
            return None

    def save_to_excel(self, videos, keyword):
        if not videos:
            print("저장할 데이터 없음")
            return ""
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "TikTok 검색 결과"
            headers = [
                "영상ID", "작성자명", "작성자ID", "팔로워수", "설명",
                "좋아요수", "댓글수", "공유수", "조회수",
                "생성일", "영상링크", "커버링크", "음악", "해시태그"
            ]
            ws.append(headers)
            for video in videos:
                ws.append([
                    video.get('video_id', ''),
                    video.get('author_name', ''),
                    video.get('author_id', ''),
                    video.get('follower_count', ''),
                    video.get('desc', ''),
                    video.get('digg_count', 0),
                    video.get('comment_count', 0),
                    video.get('share_count', 0),
                    video.get('play_count', 0),
                    video.get('create_time', ''),
                    video.get('video_url', ''),
                    video.get('cover_url', ''),
                    video.get('music_title', ''),
                    ','.join(video.get('hashtags', [])),
                ])
            filename = f"TikTok_{keyword}_{len(videos)}개.xlsx"
            wb.save(filename)
            print(f"저장 완료: {filename}")
            return filename
        except Exception as e:
            print(f"Excel 저장 실패: {e}")
            return ""

async def main():
    crawler = TikTokCrawler()
    max_attempts = 10
    attempt = 0
    keyword = input('해시태그(예: fashion) 입력: ')
    limit = int(input('수집 개수 입력 (최대 50개 권장): '))
    while attempt < max_attempts:
        try:
            await crawler.create_sessions(num_sessions=1, use_proxy=True)
            videos = await crawler.crawl_hashtag(keyword, limit)
            crawler.save_to_excel(videos, keyword)
            print("크롤링 성공!")
            break
        except Exception as e:
            attempt += 1
            print(f"[{attempt}/{max_attempts}] 크롤링 실패, 프록시 변경 후 재시도... 에러: {e}")
            await asyncio.sleep(2)
    else:
        print("여러 번 시도했지만 크롤링 실패. 프록시를 확인하거나 VPN/유료 프록시를 고려하세요.")

if __name__ == "__main__":
    asyncio.run(main())
