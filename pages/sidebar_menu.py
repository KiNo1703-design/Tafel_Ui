from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from pages.device_creation_page import DeviceCreationPage

class SidebarMenu(BasePage):
    DEVICE_RELEASE_MENU = (By.XPATH, "//span[@class='sidebar__text' and text()='Выпуск устройств']")
    
    def click_device_release(self):
        print("🖱️ Клик по меню 'Выпуск устройств'")
        self.click(self.DEVICE_RELEASE_MENU)
        return DeviceCreationPage(self.driver)