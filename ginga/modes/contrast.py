#
# contrast.py -- mode for setting contrast
#
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
"""Contrast Mode enables bindings that can adjust the contrast of
an image in a Ginga image viewer.

Enter the mode by
-----------------
* Space, then "t"

Exit the mode by
----------------
* Esc

Default bindings in mode
------------------------
* T : restore contrast to defaults
* left drag : adjust contrast
  * Interactive shift/stretch colormap (aka contrast and bias).
  * Moving left/right controls shift, up/down controls stretch.
  * Release button when satisfied with the contrast.
* right click : restore contrast to defaults

"""
import numpy as np

from ginga.modes.mode_base import Mode


class ContrastMode(Mode):

    def __init__(self, viewer, settings=None):
        super().__init__(viewer, settings=settings)

        self.actions = dict(
            dmod_contrast=['__t', None, None],

            kp_contrast_restore=['T', 'contrast+t', 'contrast+T'],

            ms_contrast=['contrast+left', 'ctrl+right'],
            ms_contrast_restore=['contrast+right', 'ctrl+middle'])

    def __str__(self):
        return 'contrast'

    @property
    def cancmap(self):
        bd = self.viewer.get_bindings()
        return bd.get_feature_allow('cmap')

    def start(self):
        pass

    def stop(self):
        self.onscreen_message(None)

    def restore_contrast(self, viewer, msg=True):
        viewer.get_settings().set(contrast=0.5, brightness=0.5)
        msg = self.settings.get('msg_cmap', msg)
        if msg:
            self.onscreen_message("Restored contrast", delay=0.5)
        return True

    def _tweak_colormap(self, viewer, x, y, mode):
        win_wd, win_ht = viewer.get_window_size()

        # translate Y cursor position as a percentage of the window
        # height into a contrast pct
        contrast_pct = np.clip(y, 0, win_ht) / float(win_ht)

        # translate X cursor position as a percentage of the window
        # width into a brightness pct
        brightness_pct = 1.0 - np.clip(x, 0, win_wd) / float(win_wd)

        with viewer.suppress_redraw:
            viewer.get_settings().set(contrast=contrast_pct,
                                      brightness=brightness_pct)

    #####  KEYBOARD ACTION CALLBACKS #####

    def kp_contrast_restore(self, viewer, event, data_x, data_y, msg=True):
        if not self.cancmap:
            return False
        event.accept()
        msg = self.settings.get('msg_cmap', msg)
        self.restore_contrast(viewer, msg=msg)

    #####  SCROLL ACTION CALLBACKS #####

    #####  MOUSE ACTION CALLBACKS #####

    def ms_contrast(self, viewer, event, data_x, data_y, msg=True):
        """Shift the colormap by dragging the cursor left or right.
        Stretch the colormap by dragging the cursor up or down.
        """
        if not self.cancmap:
            return False
        event.accept()
        msg = self.settings.get('msg_contrast', msg)

        x, y = self.get_win_xy(viewer)

        if event.state == 'move':
            self._tweak_colormap(viewer, x, y, 'preview')

        elif event.state == 'down':
            self._start_x, self._start_y = x, y
            if msg:
                self.onscreen_message(
                    "Shift and stretch colormap (drag mouse)", delay=1.0)
        else:
            self.onscreen_message(None)

    def ms_contrast_restore(self, viewer, event, data_x, data_y, msg=True):
        """An interactive way to restore the colormap contrast settings after
        a warp operation.
        """
        if not self.cancmap:
            return False
        event.accept()
        if event.state == 'down':
            self.restore_contrast(viewer, msg=msg)
