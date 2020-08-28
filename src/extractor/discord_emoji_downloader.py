# coding: UTF-8
# title: Discord 서버 커스텀 이모지 다운로드
# author: SaidBySolo

"""
MIT License

Copyright (c) 2020 SaidBySolo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import requests


@Downloader.register
class DownloaderDiscordEmoji(Downloader):
    type = "discord"

    def init(self):
        self.url = self.url.replace("discord_", "")

    @property
    def id(self):
        return self.url

    def read(self):
        base_url = "https://cdn.discordapp.com/emojis/"

        token_guild_id_list = self.url.split(
            "/"
        )  # 값을 어떻게 받을지 몰라서 일단 나눴어요. discord_이메일/비밀번호/서버아이디 이런식으로 받게 해놨어요.
        email = token_guild_id_list[0]
        password = token_guild_id_list[1]
        guild_id = token_guild_id_list[2]

        response = self.post_account_info(email, password)
        account_info = response.json()
        if response.status_code == 400:
            if account_info.get("captcha_key"):
                raise Exception(
                    "먼저 웹 또는 디스코드 앱에서 로그인하신후 캡차를 인증해주세요."
                )  # 메세지 박스 return하니까 멈춰서 raise로 해놨어요
            else:
                raise Exception("이메일 또는 비밀번호가 잘못되었습니다. 확인후 다시 시도해주세요.")
        else:
            token = account_info["token"]

        guild_info = self.get_emoji_list(token, int(guild_id))  # 토큰과 함께 get요청함

        for emoji in guild_info["emojis"]:  # 이모지 리스트로 가져옴
            if emoji["animated"] is True:  # 만약 gif면 gif 다운로드
                param = emoji["id"] + ".gif"
            else:  # 아닐경우 png로
                param = emoji["id"] + ".png"

            self.title = f'{guild_info["name"]}({guild_info["id"]})'  # 폴더 이름은 서버 이름, id
            self.urls.append(base_url + param + "?v=1")  # 인자 합치기

    def get_emoji_list(self, token: str, guild_id: int) -> dict:
        response = requests.get(
            f"https://discordapp.com/api/v6/guilds/{guild_id}",
            headers={"Authorization": token},
        )
        # if response.status_code == 401:
        #    response = requests.get(
        #        f"https://discordapp.com/api/v6/guilds/{guild_id}",
        #        headers={"Authorization": f"Bot {token}"},
        #    )

        guild_info = response.json()
        return guild_info

    def post_account_info(self, email: str, password: str) -> dict:
        response = requests.post(
            "https://discordapp.com/api/v8/auth/login",
            json={
                "email": email,
                "password": password,
                "undelete": False,
                "captcha_key": None,
                "login_source": None,
                "gift_code_sku_id": None,
            },
        )

        return response
