"""Browser page-object helpers that follow the guided UI, without changing app state."""
class GuidedFlow:
    def wait_idle(self):
        self.page.locator('#chapter-loading').wait_for(state='hidden')
    def open_menu(self):
        if not self.page.locator('#main-menu').is_visible():self.page.locator('#menu-toggle').click()
    def go_step(self,step):
        self.wait_idle()
        if self.page.locator('#practice-view').is_visible():self.page.locator('#game-change-setup').click()
        self.page.locator('#setup-view').wait_for(state='visible')
        current=int(self.page.locator('[data-wizard-step]:visible').get_attribute('data-wizard-step'))
        while current>step:self.page.locator('#wizard-back').click();current-=1
        while current<step:
            if self.page.locator('#wizard-next').is_disabled():raise AssertionError('Setup has no valid selection')
            self.page.locator('#wizard-next').click();current+=1
        if step==1 and self.page.locator('#wizard-area-details').is_visible():
            self.page.locator('#wizard-area-details').evaluate('el=>el.open=true')
    def configure_topic(self,topic):
        if self.page.locator('#home-view').is_visible():self.page.locator(f'[data-start="{topic}"]').click()
        else:
            self.go_step(0);self.page.locator(f'[data-wizard-topic="{topic}"]').click();self.page.locator('#wizard-next').click()
        self.go_step(1)
    def finish_setup(self,mode=None):
        if mode is not None:
            self.go_step(2);self.page.locator(f'[data-mode="{mode}"]').click()
        self.go_step(4);self.page.locator('#start-button').click();self.wait_idle()
        self.page.locator('#practice-view').wait_for(state='visible')
    def open_settings(self):
        if self.page.locator('#practice-view').is_visible():self.page.locator('#game-map-settings').click()
        else:self.open_menu();self.page.locator('[data-nav="settings"]').click()
    def open_progress(self):
        if self.page.locator('#progress-open').is_visible():self.page.locator('#progress-open').click()
        else:self.open_menu();self.page.locator('[data-nav="progress"]').click()
    def close_dialog(self,name):self.page.locator('#'+name+'-dialog .dialog-close').click()
