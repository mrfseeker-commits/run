import unittest

from weather_app import NaverCompareFetcher


class NaverCompareFetcherTest(unittest.TestCase):
    def test_parse_hourly_services_filters_04_to_08(self):
        html = (
            "<script>"
            'var blockApiResult = {"success":true,"results":{"choiceResult":{'
            '"compareHourlyFcast~~1":{"domesticHourlyListMap":{'
            '"TWC":['
            '{"aplYmd":"20260709","aplTm":"03","wetrTxt":"흐림","tmpr":26.0,"rainProb":30,"fcastYmdt":"20260709150100"},'
            '{"aplYmd":"20260709","aplTm":"04","wetrTxt":"비","tmpr":25.0,"rainProb":80,"rainAmt":"1.00","windDrctnName":"남동풍","fcastYmdt":"20260709150100"},'
            '{"aplYmd":"20260709","aplTm":"08","wetrTxt":"구름많음","tmpr":27.0,"rainProb":20,"rainAmt":"0.00","windDrctnName":"동풍","fcastYmdt":"20260709150100"},'
            '{"aplYmd":"20260709","aplTm":"09","wetrTxt":"맑음","tmpr":28.0,"rainProb":10,"fcastYmdt":"20260709150100"},'
            '{"aplYmd":"20260710","aplTm":"04","wetrTxt":"맑음","tmpr":22.0,"rainProb":0,"fcastYmdt":"20260709150100"}'
            "],"
            '"ACCUWEATHER":['
            '{"aplYmd":"20260709","aplTm":"04","wetrTxt":"소나기","tmpr":24.0,"rainProb":90,"snowAmt":"0.00","windDrctnName":"남풍","fcastYmdt":"20260709153000"}'
            "]"
            "}}"
            "}}};"
            "</script>"
        )

        services = NaverCompareFetcher.parse_hourly_services(html, start_hour=4, end_hour=8)

        self.assertEqual([service["provider"] for service in services], ["웨더채널", "아큐웨더"])
        self.assertEqual([row["time"] for row in services[0]["rows"]], ["07/09 04:00", "07/09 08:00"])
        self.assertEqual(services[0]["rows"][0]["weather"], "비")
        self.assertEqual(services[0]["rows"][0]["rain_probability"], "80%")
        self.assertEqual(services[1]["rows"][0]["temperature"], "24.0℃")
        self.assertEqual(services[1]["updated_at"], "2026-07-09 15:30")

    def test_parse_hourly_services_uses_requested_target_date(self):
        html = (
            "<script>"
            'var blockApiResult = {"success":true,"results":{"choiceResult":{'
            '"compareHourlyFcast~~1":{"domesticHourlyListMap":{'
            '"TWC":['
            '{"aplYmd":"20260710","aplTm":"07","wetrTxt":"흐림","tmpr":24.0,"rainProb":9,"fcastYmdt":"20260710051200"},'
            '{"aplYmd":"20260710","aplTm":"08","wetrTxt":"흐림","tmpr":25.0,"rainProb":11,"fcastYmdt":"20260710051200"},'
            '{"aplYmd":"20260711","aplTm":"04","wetrTxt":"비","tmpr":22.0,"rainProb":60,"fcastYmdt":"20260710051200"},'
            '{"aplYmd":"20260711","aplTm":"05","wetrTxt":"비","tmpr":22.0,"rainProb":60,"fcastYmdt":"20260710051200"},'
            '{"aplYmd":"20260711","aplTm":"06","wetrTxt":"흐림","tmpr":23.0,"rainProb":30,"fcastYmdt":"20260710051200"},'
            '{"aplYmd":"20260711","aplTm":"07","wetrTxt":"흐림","tmpr":24.0,"rainProb":30,"fcastYmdt":"20260710051200"},'
            '{"aplYmd":"20260711","aplTm":"08","wetrTxt":"맑음","tmpr":25.0,"rainProb":10,"fcastYmdt":"20260710051200"}'
            "],"
            '"KMA":['
            '{"aplYmd":"20260711","aplTm":"04","wetrTxt":"흐림","tmpr":22.0,"rainProb":30,"fcastYmdt":"20260710050000"}'
            "]"
            "}}"
            "}}};"
            "</script>"
        )

        services = NaverCompareFetcher.parse_hourly_services(
            html,
            start_hour=4,
            end_hour=8,
            target_date="20260711",
        )

        self.assertEqual([service["provider_code"] for service in services], ["TWC"])
        self.assertEqual(
            [row["time"] for row in services[0]["rows"]],
            ["07/11 04:00", "07/11 05:00", "07/11 06:00", "07/11 07:00", "07/11 08:00"],
        )
        self.assertEqual(services[0]["rows"][0]["rain_probability"], "60%")


if __name__ == "__main__":
    unittest.main()
