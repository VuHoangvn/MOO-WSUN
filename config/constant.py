import math

class Constants:
    anpha_1 = 0.65
    S = 0.5
    C = 0.5
    beta_1 = 1.2748 - 0.519 * S - 0.512 * C
    beta_2 = 1.3379 - 0.63 * S - 0.166 * C
    pb = 1.3
    ps = 2.66
    mv = 0.1
    esp_w0 = 80.36
    esp_w8 = 4.9
    t_w = 2
    f = 300
    muy_0 = 12.57 * pow(10, -7)
    muy_r = 12.57 * pow(10, -7)

    @classmethod
    def get_esp_s(cls):
        return pow(1.01 + 0.44 * cls.ps, 2) - 0.0062

    @classmethod
    def get_sigma_eff(cls):
        return (0.0467 + 0.224 * cls.pb - 0.411 * cls.S + 0.6614 * cls.C)

    @classmethod
    def get_esp_fw1(cls):
        return (cls.esp_w8 + (cls.esp_w0 - cls.esp_w8) / (1 + pow(2 * 3.14 * cls.f * cls.t_w, 2)))

    @classmethod
    def get_esp_1_or_0(cls):
        return (1.15 * pow(1 + cls.pb / cls.ps * pow(cls.get_esp_s(), cls.anpha_1) + pow(cls.mv, cls.beta_1) * pow(cls.get_esp_fw1(), cls.anpha_1) - cls.mv, 1 / cls.anpha_1) - 0.68)

    @classmethod
    def get_esp_fw2(cls):
        return (2 * 3.14 * cls.f * cls.t_w * (cls.esp_w0 - cls.esp_w8) / (1 + pow(2 * 3.14 * cls.f * cls.t_w, 2)) + cls.get_sigma_eff() * (cls.ps - cls.pb) / (2 * 3.14 + cls.get_esp_1_or_0() * cls.ps * cls.mv))

    @classmethod
    def get_esp_2(cls):
        return 2 * 3.14 * cls.f * cls.t_w * (cls.esp_w0 - cls.esp_w8) / (1 + pow(2 * 3.14 * cls.f * cls.t_w, 2)) + cls.get_sigma_eff() * (cls.ps - cls.pb) / (2 * 3.14 + cls.get_esp_1_or_0() * cls.ps * cls.mv)

    @classmethod
    def get_anpha(cls):
        return (2 * 3.14 * cls.f * math.sqrt(0.5 * cls.muy_r * cls.muy_0 * pow(cls.get_esp_1_or_0(), 2) * (math.sqrt(1 + pow(cls.get_esp_2() / cls.get_esp_1_or_0(), 2)) - 1)))

    @classmethod
    def get_beta(cls):
        return (2 * 3.14 * cls.f * math.sqrt(0.5 * cls.muy_r * cls.muy_0 * pow(cls.get_esp_1_or_0(), 2) * (math.sqrt(1 + pow(cls.get_esp_2() / cls.get_esp_1_or_0(), 2)) + 1)))
