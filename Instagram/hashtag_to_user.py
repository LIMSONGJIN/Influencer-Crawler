import requests
import pandas as pd
import time
import json
from urllib.parse import quote
from cookie_getter import get_instagram_cookies
import os
from fake_useragent import UserAgent
import random

USER_AGENTS = UserAgent()

def cookie_dict_to_str(cookie_dict):
    return "; ".join(f"{k}={v}" for k, v in cookie_dict.items())

cookie_file_path = "ig_cookies.json"
if not os.path.exists(cookie_file_path):
    print("[INFO] 쿠키 파일이 존재하지 않습니다. Instagram 로그인 정보를 입력해주세요.")
    username = input("Instagram 아이디: ").strip()
    password = input("Instagram 비밀번호: ").strip()
    try:
        get_instagram_cookies(username, password, save_path=cookie_file_path)
        print("[INFO] 쿠키 파일이 생성되었습니다.")
    except Exception as e:
        print("[에러] 쿠키 생성 실패:", e)

try:
    with open(cookie_file_path, "r") as f:
        MY_INSTAGRAM_COOKIES = json.load(f)
    cookie_header_str = cookie_dict_to_str(MY_INSTAGRAM_COOKIES)
except Exception as e:
    print("[에러] 쿠키 파일(ig_cookies.json) 로딩 실패:", e)
    cookie_header_str = ""

HEADERS = {
    "x-ig-app-id": "936619743392459",
    "User-Agent": USER_AGENTS.random,
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "cookie": cookie_header_str   # ← 쿠키 자동 주입
}

# 1. parse_post_node 함수 추가 (코드 상단 utils 부분에)
def parse_post_node(node):
    """
    GraphQL에서 넘어온 post node에서 릴스/게시물 등 정보 추출
    """
    media_product_type = node.get('media_product_type', '')
    shortcode = node.get('shortcode', '')
    is_reel = (media_product_type == 'REELS') or ('/reel/' in f"/{shortcode}/")
    like_count = node.get('edge_media_preview_like', {}).get('count', 0)
    comment_count = node.get('edge_media_to_comment', {}).get('count', 0)
    view_count = node.get('video_view_count', None)
    media_type = node.get('__typename', None) or node.get('typename', None)
    thumbnail_url = node.get('display_url', '')
    media_url = thumbnail_url
    video_url = node.get('video_url', None)
    caption = ""
    try:
        caption = node.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', '')
    except Exception:
        pass
    post_type = "reel" if is_reel else "post"
    return {
        'id': node.get('id'),
        'shortcode': shortcode,
        'is_reel': is_reel,
        'post_type': post_type,
        'media_type': media_type,
        'caption': caption,
        'like_count': like_count,
        'comment_count': comment_count,
        'view_count': view_count,
        'thumbnail_url': thumbnail_url,
        'media_url': media_url,
        'video_url': video_url,
        'taken_at_timestamp': node.get('taken_at_timestamp')
    }

def get_recent_posts_by_tag(tag, max_count=50):
    posts = []
    tag_encoded = quote(tag)
    url = f"https://i.instagram.com/api/v1/tags/web_info/?tag_name={tag_encoded}"
    for attempt in range(3):
        try:
            HEADERS["User-Agent"] = USER_AGENTS.random
            resp = requests.get(url, headers=HEADERS)
            if resp.status_code != 200:
                print(f"[{tag_encoded}] 게시물 수집 실패 (status: {resp.status_code})")
                return posts
            data = resp.json()
            print(f"[DEBUG] API 응답(일부): {str(data)[:300]}")
            with open(f"ig_tag_{tag_encoded}_api_response.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)    
            # 1차 시도: sections
            sections = data.get("data", {}).get("top", {}).get("sections", [])
            if not sections:
                # 2차 시도: recent
                sections = data.get("data", {}).get("recent", {}).get("sections", [])
            if not sections:
                # 3차 시도: backup - layout_content.medias만 뽑기
                medias = data.get("data", {}).get("top", {}).get("layout_content", {}).get("medias", [])
                posts.extend(medias)
                medias2 = data.get("data", {}).get("recent", {}).get("layout_content", {}).get("medias", [])
                posts.extend(medias2)
                print(f"[{tag_encoded}] fallback로 medias에서 {len(posts)}개 추출")
                return posts[:max_count]
            medias = []
            for sec in sections:
                medias.extend(sec.get("layout_content", {}).get("medias", []))
            posts.extend(medias)
            return posts[:max_count]
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"[{tag_encoded}] 요청 또는 JSON 파싱 실패: {e} (재시도 {attempt+1}/3)")
            time.sleep(random.uniform(2,5))
        except Exception as e:
            print(f"[{tag_encoded}] 예기치 않은 오류: {e} (재시도 {attempt+1}/3)")
            time.sleep(random.uniform(2,5))
    return posts

def extract_usernames_from_posts(posts):
    usernames = set()
    for post in posts:
        media = post.get('media', {})
        user = media.get('user', {})
        username = user.get('username')
        if username:
            usernames.add(username)
    return list(usernames)

# def fetch_recent_posts_graphql(user_id, count=12):
#     '''
#     인스타그램 GraphQL API로 최근 게시물 리스트 가져오기 (공개계정 한정)
#     '''
#     url = 'https://www.instagram.com/graphql/query/'
#     params = {
#         'query_hash': '003056d32c2554def87228bc3fd9668a',
#         'variables': json.dumps({
#             'id': str(user_id),
#             'first': count
#         })
#     }
#     for attempt in range(3):
#         try:
#             HEADERS["User-Agent"] = USER_AGENTS.random
#             resp = requests.get(url, headers=HEADERS, params=params)
#             if resp.status_code != 200:
#                 print(f"[GraphQL] posts 가져오기 실패 (status {resp.status_code})")
#                 return []
#             edges = resp.json()["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
#             return edges
#         except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
#             print(f"[GraphQL] 요청 또는 파싱 오류: {e} (재시도 {attempt+1}/3)")
#             time.sleep(random.uniform(2,5))
#         except Exception as e:
#             print(f"[GraphQL] 예기치 않은 오류: {e} (재시도 {attempt+1}/3)")
#             time.sleep(random.uniform(2,5))
#     return []

#
# def fetch_recent_posts_graphql_all(user_id, total_count=100):
#     '''
#     페이지네이션 방식으로 인스타그램 GraphQL API에서 최근 게시물 모두 가져오기 (공개계정 한정)
#     '''
#     url = 'https://www.instagram.com/graphql/query/'
#     query_hash = 'b3055c01b4b222b8a47dc12b090e4e64'
#     posts = []
#     has_next_page = True
#     end_cursor = None
#
#     while has_next_page and len(posts) < total_count:
#         variables = {
#             'id': str(user_id),
#             'first': min(50, total_count - len(posts))
#         }
#         if end_cursor:
#             variables['after'] = end_cursor
#
#         params = {
#             'query_hash': query_hash,
#             'variables': json.dumps(variables)
#         }
#         for attempt in range(3):
#             try:
#                 HEADERS["User-Agent"] = USER_AGENTS.random
#                 resp = requests.get(url, headers=HEADERS, params=params)
#                 if resp.status_code != 200:
#                     print(f"[GraphQL] posts 가져오기 실패 (status {resp.status_code})")
#                     break
#                 data = resp.json()
#                 # GraphQL 응답을 username별로 JSON으로 저장 (user_id 기준)
#                 with open(f"ig_graphql_{user_id}_raw.json", "w", encoding="utf-8") as f:
#                     json.dump(data, f, ensure_ascii=False, indent=2)
#                 edges = data["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
#                 page_info = data["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]
#                 # 변경: parse_post_node 결과만 저장
#                 for edge in edges:
#                     node = edge.get('node', {})
#                     parsed = parse_post_node(node)
#                     posts.append(parsed)
#                 has_next_page = page_info.get("has_next_page", False)
#                 end_cursor = page_info.get("end_cursor", None)
#                 break
#             except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
#                 print(f"[GraphQL] 요청 또는 파싱 오류: {e} (재시도 {attempt+1}/3)")
#                 time.sleep(random.uniform(2,5))
#             except Exception as e:
#                 print(f"[GraphQL] 예기치 않은 오류: {e} (재시도 {attempt+1}/3)")
#                 time.sleep(random.uniform(2,5))
#         else:
#             # 3회 모두 실패하면 루프 탈출
#             break
#
#     return posts[:total_count]

def fetch_recent_posts_rest_api(username, user_id, max_count=100, headers=None, base_dir="."):
    import os, time, json
    all_posts = []
    next_max_id = None
    for _ in range((max_count // 12) + 2):
        posts_url = f"https://i.instagram.com/api/v1/feed/user/{user_id}/?count=12"
        if next_max_id:
            posts_url += f"&max_id={next_max_id}"
        posts_headers = headers.copy()
        posts_headers["Referer"] = f"https://www.instagram.com/{username}/"
        resp = requests.get(posts_url, headers=posts_headers)
        if resp.status_code == 200:
            posts_data = resp.json()
            items = posts_data.get("items", [])
            all_posts.extend(items)
            next_max_id = posts_data.get("next_max_id")
            print(f"누적 {len(all_posts)}개 수집 (이번에 {len(items)}개)")
            if not next_max_id or not items or len(all_posts) >= max_count:
                break
            time.sleep(1)
        else:
            print(f"[ERROR] 게시물 status_code: {resp.status_code}, message: {resp.text}")
            break
    all_posts = all_posts[:max_count]
    posts_file_path = os.path.join(base_dir, f"ig_posts_{username}_max{max_count}.json")
    with open(posts_file_path, "w", encoding="utf-8") as f:
        json.dump({"items": all_posts}, f, ensure_ascii=False, indent=2)
    print(f"최종 저장된 게시물 개수: {len(all_posts)}개")
    return all_posts

def scrape_instagram_profile(username):
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    for attempt in range(3):
        try:
            HEADERS["User-Agent"] = USER_AGENTS.random
            resp = requests.get(url, headers=HEADERS)
            if resp.status_code != 200:
                print(f"[{username}] 프로필 수집 실패 (status: {resp.status_code})")
                return None
            # ★ 추가: 전체 API 응답을 username별로 저장
            with open(f"ig_profile_{username}_raw.json", "w", encoding="utf-8") as f:
                json.dump(resp.json(), f, ensure_ascii=False, indent=2)
            data = resp.json().get('data', {}).get('user', {})

            if not data:
                print(f"[{username}] 데이터 없음 (존재X/비공개/차단일 수 있음)")
                return None

            profile_info = {
                'username': username,
                'full_name': data.get('full_name', ''),
                'bio': data.get('biography', ''),
                'is_verified': data.get('is_verified', False),
                'is_private': data.get('is_private', False),
                'followers': data.get('edge_followed_by', {}).get('count', 0),
                'following': data.get('edge_follow', {}).get('count', 0),
                'posts': data.get('edge_owner_to_timeline_media', {}).get('count', 0),
                'profile_pic_url': data.get('profile_pic_url_hd', ''),
                'category': data.get('category_name', ''),
            }
            user_id = data.get('id', None)
            recent_posts = data.get('edge_owner_to_timeline_media', {}).get('edges', [])
            print(f"[DEBUG] {username} recent_posts 개수: {len(recent_posts)}")

            # recent_posts가 없을 경우 REST API(i.instagram.com)로 100개 수집
            if (not recent_posts) and user_id and (not profile_info['is_private']):
                print(f"[{username}] REST API로 최근 게시물 fetch 시도 (최대 100개, i.instagram.com 방식)")
                recent_posts_raw = fetch_recent_posts_rest_api(
                    username, user_id, max_count=100, headers=HEADERS, base_dir="."
                )
                print(f"[DEBUG] {username} REST API recent_posts 개수: {len(recent_posts_raw)}")
                # 필요 시 가공
                parsed_posts = []
                for post in recent_posts_raw:
                    parsed = {
                        'id': post.get('id'),
                        'shortcode': post.get('code', ''),
                        'is_reel': post.get('media_type', '') == 2,
                        'post_type': 'reel' if post.get('media_type', '') == 2 else 'post',
                        'media_type': post.get('media_type', ''),
                        'caption': post.get('caption', {}).get('text', ''),
                        'like_count': post.get('like_count', 0),
                        'comment_count': post.get('comment_count', 0),
                        'view_count': post.get('view_count', None),
                        'thumbnail_url': post.get('image_versions2', {}).get('candidates', [{}])[0].get('url', ''),
                        'media_url': post.get('image_versions2', {}).get('candidates', [{}])[0].get('url', ''),
                        'video_url': post.get('video_versions', [{}])[0].get('url', None) if post.get('video_versions') else None,
                        'taken_at_timestamp': post.get('taken_at', None)
                    }
                    parsed_posts.append(parsed)
                recent_posts = parsed_posts
            else:
                # recent_posts가 API에서 바로 넘어온 경우, parse_post_node로 변환 필요
                if recent_posts:
                    parsed_posts = []
                    for post in recent_posts:
                        node = post.get('node', {})
                        parsed = parse_post_node(node)
                        parsed_posts.append(parsed)
                    recent_posts = parsed_posts

            if recent_posts and profile_info['followers'] > 0:
                total_likes = sum(post.get('like_count', 0) for post in recent_posts)
                total_comments = sum(post.get('comment_count', 0) for post in recent_posts)
                count_posts = len(recent_posts)
                avg_engagement = (total_likes + total_comments) / count_posts if count_posts > 0 else 0
                engagement_rate = (avg_engagement / profile_info['followers']) * 100 if profile_info['followers'] > 0 else 0.0
                profile_info['engagement_rate'] = round(engagement_rate, 2)
            else:
                profile_info['engagement_rate'] = 0.0 if profile_info['followers'] > 0 else None

            profile_info['ai_grade'], profile_info['ai_score'] = get_ai_grade(
                profile_info.get('followers', 0), profile_info.get('engagement_rate', 0.0)
            )
            # 3. recent_posts_raw는 parse 결과로 저장
            profile_info['recent_posts_raw'] = recent_posts
            return profile_info
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"[{username}] 요청 또는 JSON 파싱 실패: {e} (재시도 {attempt+1}/3)")
            time.sleep(random.uniform(2,5))
        except Exception as e:
            print(f"[{username}] 예기치 않은 오류: {e} (재시도 {attempt+1}/3)")
            time.sleep(random.uniform(2,5))
    return None

def get_ai_grade(followers, engagement_rate):
    if followers is None:
        followers = 0
    if engagement_rate is None:
        engagement_rate = 0.0
    if followers >= 1000000 and engagement_rate >= 4:
        return "S", 92
    elif followers >= 100000 and engagement_rate >= 2:
        return "A", 85
    elif followers >= 10000 and engagement_rate >= 1:
        return "B", 78
    else:
        return "C", 70

def main():
    print("인스타그램 인플루언서 카테고리(해시태그) 크롤러")
    category = input("크롤링할 카테고리(해시태그, 예: fashion, 헬스, 여행 등)를 입력하세요: ").strip().replace("#", "")
    if not category:
        print("카테고리를 입력해주세요.")
        return

    try:
        max_count = int(input("수집할 게시물(작성자) 최대 개수 (기본 50): ") or "50")
    except:
        max_count = 50

    try:
        sleep_sec = float(input("요청 간 딜레이(초, 기본 2.0): ") or "2.0")
    except:
        sleep_sec = 2.0

    print(f"[INFO] 해시태그 #{category} 최신 게시물 {max_count}개 수집 중...")
    posts = get_recent_posts_by_tag(category, max_count=max_count)
    print(f"[INFO] 게시물 {len(posts)}개 수집")

    usernames = extract_usernames_from_posts(posts)
    print(f"[INFO] 유니크 계정 {len(usernames)}개 추출")

    results = []
    recent_posts_json = {}
    for i, uname in enumerate(usernames, 1):
        print(f"[{i}/{len(usernames)}] {uname} 프로필 크롤링 중...")
        profile = scrape_instagram_profile(uname)
        if profile:
            results.append(profile)
            recent_posts_json[uname] = profile.get('recent_posts_raw', [])
        time.sleep(random.uniform(sleep_sec, sleep_sec + 2.5))

    if results:
        fname = f"insta_{category}_profiles.csv"
        columns = [
            'username', 'full_name', 'bio', 'is_verified', 'is_private',
            'followers', 'following', 'posts', 'profile_pic_url', 'category',
            'engagement_rate', 'ai_grade', 'ai_score'
        ]
        df = pd.DataFrame(results)
        # 누락된 컬럼 있을 경우 대비
        for col in columns:
            if col not in df.columns:
                df[col] = None
        df = df[columns]
        df.to_csv(fname, index=False, encoding='utf-8-sig')
        print(f"[INFO] {len(results)}개 계정 정보가 {fname}에 저장되었습니다.")

        recent_posts_fname = f"insta_{category}_recent_posts_full.json"
        with open(recent_posts_fname, "w", encoding="utf-8") as f:
            json.dump(recent_posts_json, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 각 계정별 최근 게시물 원본 데이터가 {recent_posts_fname}에 저장되었습니다.")
    else:
        print("수집된 프로필 데이터가 없습니다.")

if __name__ == "__main__":
    main()