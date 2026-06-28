"""
Meta Manager Skill
Instagram posts, Facebook posts, and Meta Ads via Graph API.
"""

import urllib.request, urllib.parse, json, os


class MetaManager:
    def __init__(self, access_token, page_id, ig_account_id, ad_account_id):
        self.token          = access_token
        self.page_id        = page_id
        self.ig_account_id  = ig_account_id
        self.ad_account_id  = ad_account_id
        self.graph          = "https://graph.facebook.com/v19.0"

    def _get(self, endpoint, params=None):
        p = {"access_token": self.token, **(params or {})}
        qs = urllib.parse.urlencode(p)
        url = f"{self.graph}/{endpoint}?{qs}"
        req = urllib.request.Request(url, headers={"User-Agent": "ZenBot/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read()), None
        except urllib.error.HTTPError as e:
            return None, f"HTTP {e.code}: {e.read().decode()}"
        except Exception as e:
            return None, str(e)

    def _post(self, endpoint, data):
        data["access_token"] = self.token
        body = urllib.parse.urlencode(data).encode()
        url  = f"{self.graph}/{endpoint}"
        req  = urllib.request.Request(url, data=body, headers={"User-Agent": "ZenBot/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read()), None
        except urllib.error.HTTPError as e:
            return None, f"HTTP {e.code}: {e.read().decode()}"
        except Exception as e:
            return None, str(e)

    # ── Instagram ─────────────────────────────────────────────────────────────

    def post_instagram_reel(self, video_url, caption):
        """Upload a reel to Instagram. video_url must be a public HTTPS URL."""
        # Step 1: create media container
        data, err = self._post(f"{self.ig_account_id}/media", {
            "media_type": "REELS",
            "video_url":  video_url,
            "caption":    caption,
            "share_to_feed": "true"
        })
        if err: return None, f"Container error: {err}"
        container_id = data.get("id")

        # Step 2: publish
        pub, err = self._post(f"{self.ig_account_id}/media_publish", {
            "creation_id": container_id
        })
        if err: return None, f"Publish error: {err}"
        return pub.get("id"), None

    def post_instagram_image(self, image_url, caption):
        data, err = self._post(f"{self.ig_account_id}/media", {
            "image_url": image_url,
            "caption":   caption
        })
        if err: return None, err
        container_id = data.get("id")
        pub, err = self._post(f"{self.ig_account_id}/media_publish", {"creation_id": container_id})
        if err: return None, err
        return pub.get("id"), None

    def get_instagram_insights(self, days=7):
        data, err = self._get(f"{self.ig_account_id}/insights", {
            "metric": "impressions,reach,profile_views,follower_count",
            "period": "day"
        })
        if err: return None, err
        return data.get("data", []), None

    # ── Facebook Page ─────────────────────────────────────────────────────────

    def post_facebook(self, message, link=None):
        payload = {"message": message}
        if link: payload["link"] = link
        data, err = self._post(f"{self.page_id}/feed", payload)
        if err: return None, err
        return data.get("id"), None

    def post_facebook_reel(self, video_url, description):
        data, err = self._post(f"{self.page_id}/videos", {
            "file_url":    video_url,
            "description": description,
            "content_tags": "Reels"
        })
        if err: return None, err
        return data.get("id"), None

    # ── Meta Ads ──────────────────────────────────────────────────────────────

    def get_campaigns(self):
        data, err = self._get(f"{self.ad_account_id}/campaigns", {
            "fields": "id,name,status,daily_budget,lifetime_budget,objective"
        })
        if err: return None, err
        return data.get("data", []), None

    def get_campaign_insights(self, campaign_id, days=7):
        data, err = self._get(f"{campaign_id}/insights", {
            "fields": "impressions,clicks,spend,ctr,cpm,reach,actions",
            "date_preset": f"last_{days}_d"
        })
        if err: return None, err
        return data.get("data", [{}])[0] if data else {}, None

    def get_all_campaigns_performance(self):
        campaigns, err = self.get_campaigns()
        if err: return None, err
        results = []
        for c in campaigns:
            insights, _ = self.get_campaign_insights(c["id"])
            results.append({**c, "insights": insights or {}})
        return results, None

    def set_campaign_status(self, campaign_id, status):
        """status: ACTIVE or PAUSED"""
        data, err = self._post(f"{campaign_id}", {"status": status})
        if err: return False, err
        return True, None

    def set_campaign_budget(self, campaign_id, daily_budget_inr):
        """daily_budget_inr in rupees — API needs paise (×100)"""
        budget_paise = int(daily_budget_inr * 100)
        data, err = self._post(f"{campaign_id}", {"daily_budget": budget_paise})
        if err: return False, err
        return True, None

    def campaigns_summary(self):
        campaigns, err = self.get_all_campaigns_performance()
        if err: return f"Error: {err}"
        lines = ["Meta Ad Campaigns:"]
        for c in campaigns:
            ins = c.get("insights") or {}
            spend = ins.get("spend", "0")
            ctr   = ins.get("ctr", "0")
            clk   = ins.get("clicks", "0")
            imp   = ins.get("impressions", "0")
            lines.append(
                f"  [{c['status']}] {c['name']}\n"
                f"    Spend: ₹{spend} | CTR: {ctr}% | Clicks: {clk} | Impressions: {imp}"
            )
        return "\n".join(lines)
