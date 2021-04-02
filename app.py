import re
from tkinter import *
from tkinter import ttk

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class Application(Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        # Web Driver
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=options)
        self.driver.implicitly_wait(4)

        # Custom close window func to close WebDriver properly
        self.master.protocol("WM_DELETE_WINDOW", self.close_window)

        self.master.title('AirBnB to HTML Card')
        self.master.iconbitmap('images/airbnb_logo.ico')
        # self.master.resizable(width=False, height=False)
        self.pack(padx=20, pady=20)

        self.create_widgets()

        self.load_default_template()

    def create_widgets(self):
        content = Frame(self, width=500, height=350)
        content.grid()
        content.columnconfigure(0, weight=10)

        self.url = StringVar()
        url_entry = Entry(content, textvariable=self.url)
        url_entry.bind('<Return>', self.submit)
        url_entry.grid(column=0, row=0, sticky='ew',
                       padx=3, pady=3, ipadx=3, ipady=3)

        submit_button = Button(content, text='Submit', command=self.submit)
        submit_button.grid(column=1, row=0, padx=3, pady=3, ipadx=1, ipady=1)

        self.status = StringVar(value='Enter a url!')
        status_label = Label(content, textvariable=self.status, justify=RIGHT)
        status_label.grid(column=0, row=1, columnspan=2,
                          sticky='e', padx=8, pady=3)

        # Output textbox & settings
        output_notebook = ttk.Notebook(content)
        output_textbox_frame = Frame(output_notebook)
        output_settings_frame = Frame(output_notebook)
        output_notebook.add(output_textbox_frame, text='Output')
        output_notebook.add(output_settings_frame, text='Settings')
        output_notebook.grid(column=0, row=2, columnspan=2, padx=3, pady=3)
        # Output
        self.output_textbox = Text(output_textbox_frame)
        self.output_textbox.grid()
        # Settings
        self.settings_textbox = Text(output_settings_frame)
        self.settings_textbox.grid()
        self.settings_small_images = IntVar()
        self.settings_small_images.set(True)  # Set default
        output_settings_checkbox = Checkbutton(
            output_settings_frame, text="Small image urls", variable=self.settings_small_images)
        output_settings_checkbox.grid(column=0, row=1, sticky='w')

        self.output_string = StringVar(
            value='\nTitle: \nHost: \nRooms: \nImage Url: ')
        output_label = Label(content, textvariable=self.output_string, justify=LEFT)
        output_label.grid(column=0, row=3, columnspan=2, sticky='w')

    def submit(self, event=None):
        '''
        Scrape listing data from airbnb

        '''
        self.status.set('Retrieving data...')
        self.output_textbox.delete('1.0', END)
        self.output_string.set('\nTitle:\nHost:\nRooms:\nImage url:')
        self.update()

        url = self.url.get()
        self.driver.get(url)

        try:
            title = self.driver.find_element_by_xpath(
                '//div[@class="_mbmcsn"]//h1[@class="_14i3z6h"]').text
            host = self.driver.find_element_by_xpath(
                '//div[@class="_tqmy57"]//div[1]').text
            rooms = self.driver.find_element_by_xpath(
                '//div[@class="_tqmy57"]//div[2]').text
            image_url = self.driver.find_element_by_xpath(
                '//div[@class="_skzmvy"]//img').get_attribute('data-original-uri')

            if self.settings_small_images.get():
                # Modify image url endpoint to get smaller images
                if not re.search('im/pictures', image_url):
                    image_url = image_url.replace('/pictures', '/im/pictures')
                clean_url = re.search(
                    '(.*pictures.*\.[^?]*)', image_url).group(0)
                image_url = clean_url + '?im_w=720'

        except Exception as e:
            print(e)
            self.status.set('Error. Please try again.')
            self.update()

        s = self.html_output(url, title, host, rooms, image_url)
        self.output_textbox.delete('1.0', END)
        self.output_textbox.insert(END, s)
        self.output_string.set(
            '\nTitle: '+title+'\nHost: '+host+'\nRooms: '+rooms+'\nImage url: '+image_url)
        self.status.set('Success!')
        return

    def load_default_template(self):
        ''' 
        Load default html template into settings 

        '''
        self.output_template = (
            '<figure class="kg-card kg-bookmark-card">'
            '<a class="kg-bookmark-container" href="{ url }">'
            '<div class="kg-bookmark-content">'
            '<div class="kg-bookmark-title">{ title }</div>'
            '<div class="kg-bookmark-description">{ host }<br>{ rooms }</div>'
            '<div class="kg-bookmark-metadata">'
            '<img class="kg-bookmark-icon" '
            'src="https://a0.muscache.com/airbnb/static/icons/android-icon-192x192-c0465f9f0380893768972a31a614b670.png">'
            '<span class="kg-bookmark-publisher">Airbnb</span>'
            '</div>'
            '</div>'
            '<div class="kg-bookmark-thumbnail">'
            '<img src="{ image_url }">'
            '</div>'
            '</a>'
            '</figure>'
        )
        self.settings_textbox.delete('1.0', END)
        self.settings_textbox.insert(END, self.output_template)
        self.update()
        return

    def html_output(self, *args):
        '''
        Insert args into output placeholders

        Input: url, title, host, rooms, image_url

        '''
        template = self.settings_textbox.get('1.0', END)
        # Populate variable fields
        for i, s in enumerate(['{ url }', '{ title }', '{ host }', '{ rooms }', '{ image_url }']):
            template = template.replace(s, args[i])

        return template

    def close_window(self):
        self.status.set('Closing app...')
        self.update()
        self.master.destroy()
        self.driver.quit()


if __name__ == '__main__':
    root = Tk()
    app = Application(master=root)
    app.mainloop()
