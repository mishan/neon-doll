;;; neon-doll-dark-theme.el --- Neon Doll Dark -*- lexical-binding: t -*-

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

;; A dark plum page: fuchsia for position, purple for the rest.
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

(deftheme neon-doll-dark
  "Neon Doll Dark.  A dark plum page: fuchsia for position, purple for the rest."
  :background-mode 'dark
  :kind 'color-scheme
  :family 'neon-doll)

(defconst neon-doll-dark-palette
  '((bg . "#0f0d14")
    (panel . "#16131d")
    (line . "#2a2438")
    (ink . "#ebe6f0")
    (muted . "#9c93ab")
    (dimmest . "#6f6880")
    (pink . "#ff2d95")
    (purple . "#b48cff")
    (string . "#e5c07b")
    (add . "#7ee787")
    (del . "#ff7b72")
    (wash . "#191522")
    (wash-strong . "#201a2c")
    (grid . "#1e1829")
    (press . "#29213a")
    (select . "#57173b")
    (wash-pink . "#351229")
    (edge-purple . "#40335a")
    (ul-purple . "#493966")
    (add-bg . "#141e1a")
    (del-bg . "#261419")
    (add-bg-hl . "#1f2f29")
    (del-bg-hl . "#3d1f28")
    (add-refine . "#1b3823")
    (del-refine . "#491e21")
    (change-bg . "#241f1e")
    (bright-red . "#f7a6a4")
    (bright-green . "#aae7b1")
    (ansi-black . "#2a2438")
    (ansi-red . "#ff7b72")
    (ansi-green . "#7ee787")
    (ansi-yellow . "#e5c07b")
    (ansi-blue . "#8ca3ff")
    (ansi-magenta . "#b48cff")
    (ansi-cyan . "#7ed9e7")
    (ansi-white . "#c4bcce")
    (ansi-bright-black . "#9c93ab")
    (ansi-bright-red . "#f7a6a4")
    (ansi-bright-green . "#aae7b1")
    (ansi-bright-yellow . "#e7cfaa")
    (ansi-bright-blue . "#b2bef9")
    (ansi-bright-magenta . "#cab0f9")
    (ansi-bright-cyan . "#aadeeb")
    (ansi-bright-white . "#ebe6f0"))
  "The Neon Doll Dark palette.")

(neon-doll-theme-apply 'neon-doll-dark neon-doll-dark-palette)

(provide-theme 'neon-doll-dark)

;;; neon-doll-dark-theme.el ends here
