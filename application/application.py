import Tkinter as tk
from Tkconstants import LEFT, RIDGE, SUNKEN, TOP, X, W, E, N, S
from Borg import Borg
from operator import itemgetter
from Carbon.QuickDraw import frame


class Application(tk.Frame, Borg):
    def __init__(self, coach):
        Borg.__init__(self)
        if coach is not None:
            self._coach = coach
            tk.Frame.__init__(self, None)
            self.grid()
            self.createWidgets()

    @classmethod
    def from_previous_instance(cls):
        return cls(None)

    def createWidgets(self):
        self._coach_control_frame = self.create_coach_control_frame()
        self._coach_control_frame.grid(row=0, column=0, sticky=W)

        # self._time_frame = self.create_time_frame(input_params)
        # self._time_frame.grid(row=1, column=0, sticky=W)

        separator = tk.Frame(self, height=2, bd=1, relief=SUNKEN)
        separator.grid(row=3, column=0, sticky=W)

        self._state_frame = self.create_state_frame()
        self._state_frame.grid(row=5, column=0, columnspan=10)

    def create_coach_control_frame(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="Coach").grid(row=0, column=0, sticky=W)
        tk.Button(frame, text='Start', command=self._coach.start).grid(row=1, column=0, sticky=W + E)
        tk.Button(frame, text='Step', command=self._coach.step).grid(row=1, column=1, sticky=W + E)
        tk.Button(frame, text='Stop', command=self._coach.stop).grid(row=1, column=2, sticky=W + E)
        tk.Button(frame, text='Quit', command=self.quit_app).grid(row=1, column=3, sticky=W + E)
        return frame

    def create_state_frame(self):
        frame = tk.Frame(self, width=200, height=200)
        label = tk.Label(frame, text="Coach State")
        label.grid(row=0, column=0)
        return frame

    def show_state(self, output_list):
        output_list = sorted(output_list, key = itemgetter('name'))
        frame = tk.Frame(self._state_frame)
        i = 1
        for item in output_list:
            j = 0
            tk.Label(frame, text="{}:{}".format('name', item['name'])).grid(row=i, column=0)
            tk.Label(frame, text="{}:{}".format('id', item['id'])).grid(row=i, column=1)
            tk.Label(frame, text="{}:{}".format('visible', item['visible'])).grid(row=i, column=2)
            j = 3
            for key in sorted(item.keys()):
                if (key != 'name') and (key != 'id') and (key != 'visible'):
                    label = tk.Label(frame, text = "{}:{}".format(key, item[key])).grid(row=i, column = j)
                    j = j + 1
            i = i + 1
        frame.grid(row=2, column=0)

    def create_time_frame(self, input_params):
        frame = tk.Frame(self)
        tk.Label(frame, text="Time").grid(row=0, column=0, stick=W)
        self.create_week_option_menu(input_params, frame)
        self.create_day_option_menu(input_params, frame)
        set_button = tk.Button(frame, text="Set", command=self.set_time)
        set_button.grid(row=1, column=4)
        return frame

    def set_time(self):
        week = int(self._week.get())
        day = int(self._day.get())
        self._coach.set_time(week, day)

    def create_week_option_menu(self, input_params, parent_frame):
        week_label = tk.Label(parent_frame, text="week")
        week_label.grid(row=1, column=0)
        begin_at = int(input_params["Time"]["begin_at_week"])
        end_at = int(input_params["Time"]["end_at_week"])
        options = []
        for i in range(begin_at, end_at + 1):
            options.append(i)
        self._week = tk.StringVar(self)
        self._week.set(begin_at)  # default value
        w = tk.OptionMenu(parent_frame, self._week, *options)
        w.grid(row=1, column=1)

    def create_day_option_menu(self, input_params, parent_frame):
        day_label = tk.Label(parent_frame, text="day")
        day_label.grid(row=1, column=2)

        begin_at = int(input_params["Time"]["begin_at_week_day"])
        end_at = int(input_params["Time"]["end_at_week_day"])
        options = []
        for i in range(begin_at, end_at + 1):
            options.append(i)
        self._day = tk.StringVar(self)
        self._day.set(begin_at)  # default value
        d = tk.OptionMenu(parent_frame, self._day, *options)
        d.grid(row=1, column=3)



    def quit_app(self):
        self._coach_runner.shutdown()
        self.quit()

    def print_string(self, string):
        print "[Application] :: received string - %s" % string

    def get_activity_assessment(self, activity_name, feature_list):
        frame = tk.Frame(self._interactive_frame)
        tk.Label(frame, text="Enter pre-intervention assessment for activity '%s'" % activity_name).grid(row=0,
                                                                                                         column=0)
        feature_entry_map = {}
        feature_row = 1
        for feature in feature_list:
            feature_frame = tk.Frame(frame)
            tk.Label(feature_frame, text=feature).grid(row=feature_row, column=0)
            entry = tk.Entry(feature_frame)
            entry.grid(row=feature_row, column=1)
            feature_frame.grid(row=feature_row, column=0)
            feature_entry_map[feature] = entry
            feature_row = feature_row + 1
        tk.Button(frame, text='Enter',
                  command=lambda: self.accept_activity_assessment_values(frame, activity_name, feature_entry_map)).grid(
            row=feature_row, column=0)
        frame.grid(row=0, column=0)

    def accept_activity_assessment_values(self, frame, activity_name, feature_entry_map):
        value_list = {}
        for feature, entry in feature_entry_map.iteritems():
            value = entry.get()
            value_list[feature] = int(value)
        data = {"id_attribute": activity_name, "key_values": value_list}
        print "[UserSim] :: assessment data for %s is %s" % (activity_name, data)
        self._input_writer.to_write = data
        frame.destroy()