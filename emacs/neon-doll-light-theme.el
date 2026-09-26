;;; neon-doll-light-theme.el --- Neon Doll Light -*- lexical-binding: t -*-

;; Copyright (C) 2026 Misha Nasledov

;; Author: Misha Nasledov <misha@nasledov.com>
;; Version: 0.1
;; Package-Requires: ((emacs "29.1"))
;; Keywords: faces, themes
;; SPDX-License-Identifier: GPL-3.0-or-later

;; This file is not part of GNU Emacs.

;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with this program.  If not, see <https://www.gnu.org/licenses/>.

;;; Commentary:

;; Plum-tinted paper: fuchsia for position, purple for the rest.
;; The faces are in neon-doll-theme-common.el; this file is the palette.
;; Tints are the translucent tokens of the design flattened onto the
;; background, and ansi-* is the Tilix palette.  The palette is written
;; from tokens.toml by tools/build-palettes.py in the source repository;
;; tools/tokens.py there shows how each value is derived.

;;; Code:

(eval-and-compile
  (require 'neon-doll-theme-common
           (expand-file-name "neon-doll-theme-common"
                             (file-name-directory (macroexp-file-name)))))

(deftheme neon-doll-light
  "Neon Doll Light.  Plum-tinted paper: fuchsia for position, purple for the rest."
  :background-mode 'light
  :kind 'color-scheme
  :family 'neon-doll)

(defconst neon-doll-light-palette
  '((bg . "#f7f4fa")
    (panel . "#ede7f3")
    (line . "#d6cce2")
    (ink . "#1a1522")
    (muted . "#5f5670")
    (dimmest . "#8d84a0")
    (pink . "#c8006a")
    (purple . "#6a3fd0")
    (string . "#8a6100")
    (add . "#1f7a33")
    (del . "#c4312a")
    (wash . "#f0ebf8")
    (wash-strong . "#eae4f6")
    (grid . "#ede7f7")
    (press . "#e3dbf4")
    (select . "#efc8e0")
    (wash-pink . "#f3e0ee")
    (edge-purple . "#cdbeed")
    (ul-purple . "#bface9")
    (add-bg . "#e8ebec")
    (del-bg . "#f3e6eb")
    (add-bg-hl . "#d9dee2")
    (del-bg-hl . "#ebd6e1")
    (add-refine . "#ccdcd2")
    (del-refine . "#edcdd0")
    (change-bg . "#efeae8")
    (bright-red . "#802627")
    (bright-green . "#1d522c")
    (ansi-black . "#d6cce2")
    (ansi-red . "#c4312a")
    (ansi-green . "#1f7a33")
    (ansi-yellow . "#8a6100")
    (ansi-blue . "#3f5cd0")
    (ansi-magenta . "#6a3fd0")
    (ansi-cyan . "#1f6e7a")
    (ansi-white . "#3c3649")
    (ansi-bright-black . "#5f5670")
    (ansi-bright-red . "#802627")
    (ansi-bright-green . "#1d522c")
    (ansi-bright-yellow . "#5d430e")
    (ansi-bright-blue . "#30408a")
    (ansi-bright-magenta . "#4a2e8a")
    (ansi-bright-cyan . "#1d4a57")
    (ansi-bright-white . "#1a1522"))
  "The Neon Doll Light palette.")

(neon-doll-theme-apply 'neon-doll-light neon-doll-light-palette)

(provide-theme 'neon-doll-light)

;;; neon-doll-light-theme.el ends here
