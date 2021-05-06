
import logging
import timeit
import traceback
import time

import gi
gi.require_version('GstBase', '1.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GstBase

Gst.init(None)


# class MyPlugin(Gst.Element):

class MyPlugin(GstBase.BaseTransform):

    __gstmeta__ = ("myplugin",
                   "Transform",
                   "Python",
                   "author")

    __gstmetadata__ = __gstmeta__

    # __gstmetadata__ = ('myplugin', 'Transform',
    #                    'Element written in python', 'author')

    _srctemplate = Gst.PadTemplate.new('src', Gst.PadDirection.SRC,
                                       Gst.PadPresence.ALWAYS,
                                       Gst.Caps.from_string("video/x-raw,format=RGB"))

    _sinktemplate = Gst.PadTemplate.new('sink', Gst.PadDirection.SINK,
                                        Gst.PadPresence.ALWAYS,
                                        Gst.Caps.from_string("video/x-raw,format=RGB"))

    __gsttemplates__ = (_srctemplate, _sinktemplate)

    __gproperties__ = {
        "model": (GObject.TYPE_PYOBJECT,
                  "model",
                  "Contains model that implements IDataTransform",
                  GObject.ParamFlags.READWRITE)
    }

    def __init__(self):
        Gst.Element.__init__(self)

        self.sinkpad = Gst.Pad.new_from_template(self._sinktemplate, 'sink')
        self.sinkpad.set_chain_function_full(self.chainfunc, None)
        self.sinkpad.set_event_function_full(self.eventfunc, None)
        self.add_pad(self.sinkpad)

        self.srcpad = Gst.Pad.new_from_template(self._srctemplate, 'src')
        self.srcpad.set_event_function_full(self.srceventfunc, None)
        self.srcpad.set_query_function_full(self.srcqueryfunc, None)
        self.add_pad(self.srcpad)

        self.model = None

    def chainfunc(self, pad, parent, buffer):

        try:
            if self.model is not None:
                item = {
                    "pad": pad,
                    "buffer": buffer,
                    "timeout": 0.01
                }
                self.model.process(**item)
        except Exception as e:
            logging.error(e)
            traceback.print_exc()

        return self.srcpad.push(buffer)

    def do_get_property(self, prop):
        if prop.name == 'model':
            return self.model
        else:
            raise AttributeError('unknown property %s' % prop.name)

    def do_set_property(self, prop, value):
        if prop.name == 'model':
            self.model = value
        else:
            raise AttributeError('unknown property %s' % prop.name)

    def eventfunc(self, pad, parent, event):
        return self.srcpad.push_event(event)

    def srcqueryfunc(self, pad, object, query):
        return self.sinkpad.query(query)

    def srceventfunc(self, pad, parent, event):
        return self.sinkpad.push_event(event)


def register(class_info):

    # def init(plugin, plugin_impl, plugin_name):
    #     print("registering type", plugin_name)
    #     type_to_register = GObject.type_register(plugin_impl)
    #     return Gst.Element.register(plugin, plugin_name, 0, type_to_register)

    # Parameters explanation
    # https://lazka.github.io/pgi-docs/Gst-1.0/classes/Plugin.html#Gst.Plugin.register_static

#  classmethod register_static(major_version, minor_version, name, description, init_func, version, license, source, package, origin)[source]
#     Parameters:

#         major_version (int) – the major version number of the GStreamer core that the plugin was compiled for, you can just use Gst.VERSION_MAJOR here
#         minor_version (int) – the minor version number of the GStreamer core that the plugin was compiled for, you can just use Gst.VERSION_MINOR here
#         name (str) – a unique name of the plugin (ideally prefixed with an application- or library-specific namespace prefix in order to avoid name conflicts in case a similar plugin with the same name ever gets added to GStreamer)
#         description (str) – description of the plugin
#         init_func (Gst.PluginInitFunc) – pointer to the init function of this plugin.
#         version (str) – version string of the plugin
#         license (str) – effective license of plugin. Must be one of the approved licenses (see Gst.PluginDesc above) or the plugin will not be registered.
#         source (str) – source module plugin belongs to
#         package (str) – shipped package plugin belongs to
#         origin (str) – URL to provider of plugin

    # __gstmeta__ = ("ivoplugin",
    #                "Transform",
    #                "Python",
    #                "author")

    version = '1.0'
    gstlicense = 'LGPL'
    origin = ''
    name = class_info.__gstmetadata__[0]
    source = class_info.__gstmetadata__[1]
    package = class_info.__gstmetadata__[0]
    description = class_info.__gstmetadata__[2]

    def init_function(plugin, userarg):
        # return init(plugin, class_info, name)
        print("register type")
        MyType = GObject.type_register(MyPlugin)
        print("register element")
        Gst.Element.register(plugin, 'myplugin', 0, MyType)
        return True

    # print("register_static", name, description, source, package)
    ok = Gst.Plugin.register_static_full(
        Gst.VERSION_MAJOR, Gst.VERSION_MINOR,
        name, description,
        init_function,
        version,
        gstlicense,
        source,
        package,
        origin,
        None)

    if not ok:
        raise ImportError("Plugin {} not registered".format(name))

    return ok


print("MyPlugin")

register(MyPlugin)

# print("registering type")
# GObject.type_register(GstPluginPy)
# __gstelementfactory__ = ("myplugin", Gst.Rank.NONE, GstPluginPy)
