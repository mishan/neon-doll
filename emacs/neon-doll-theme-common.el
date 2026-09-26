;;; neon-doll-theme-common.el --- Faces shared by the Neon Doll themes -*- lexical-binding: t -*-

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

;; The faces for `neon-doll-dark' and `neon-doll-light', written once.  Each
;; theme file holds only its palette and hands it to
;; `neon-doll-theme-apply'.
;;
;; The rules, which are the same in both variants:
;;
;; - Fuchsia (pink) means position: the cursor, the current line number,
;;   the current isearch match, the matching paren, the current completion
;;   candidate, the rail over the active mode line and the current tab.
;;   It is also the keyword color, as it is on the site the palette comes
;;   from.  It is never emphasis.
;; - Purple is the resting interactive color: links, keys, the minibuffer
;;   prompt, other search matches.  The two roles never swap.
;; - Four syntax colors and no more.  Pink keywords, purple literals and
;;   types, string strings, muted italic comments; everything else is ink.
;; - Headings are the default family at weight normal and height 1.0.
;; - Diff lines carry both a text color and a full-width tint, and the +/-
;;   marker stays.
;; - Every tint is a solid color: the site's translucent tokens flattened
;;   onto the background.  tools/tokens.py in the source repository
;;   derives them, and tools/scheme-colors.py reports their contrast.

;;; Code:

(require 'let-alist)

;;;###autoload
(when load-file-name
  (add-to-list 'custom-theme-load-path
               (file-name-as-directory (file-name-directory load-file-name))))

(defun neon-doll-theme--faces (palette)
  "Return the face specs for PALETTE, an alist of color names to hex values."
  (let-alist palette
    `(
      ;; --- base -------------------------------------------------------------
      (default ((t (:foreground ,.ink :background ,.bg))))
      (cursor ((t (:background ,.pink))))
      (fringe ((t (:foreground ,.dimmest :background ,.bg))))
      (region ((t (:background ,.select :distant-foreground ,.ink :extend t))))
      (secondary-selection ((t (:background ,.press :extend t))))
      (highlight ((t (:foreground ,.pink :background ,.wash-pink))))
      (hl-line ((t (:background ,.wash :extend t))))
      (shadow ((t (:foreground ,.dimmest))))
      (escape-glyph ((t (:foreground ,.purple))))
      (homoglyph ((t (:foreground ,.purple))))
      (nobreak-space ((t (:foreground ,.purple :underline t))))
      (nobreak-hyphen ((t (:foreground ,.purple))))
      (trailing-whitespace ((t (:background ,.del-bg))))
      (fill-column-indicator ((t (:foreground ,.line))))
      (vertical-border ((t (:foreground ,.line))))
      (window-divider ((t (:foreground ,.line))))
      (window-divider-first-pixel ((t (:foreground ,.line))))
      (window-divider-last-pixel ((t (:foreground ,.line))))
      (internal-border ((t (:background ,.bg))))
      (child-frame-border ((t (:background ,.line))))
      (tooltip ((t (:foreground ,.ink :background ,.panel))))
      (error ((t (:foreground ,.del))))
      (warning ((t (:foreground ,.string))))
      (success ((t (:foreground ,.add))))
      (bold ((t (:weight bold))))
      (italic ((t (:slant italic))))

      ;; --- line numbers: the current one is where you are -------------------
      (line-number ((t (:foreground ,.dimmest :background ,.bg))))
      (line-number-current-line ((t (:foreground ,.pink :background ,.wash))))
      (line-number-major-tick ((t (:foreground ,.muted :background ,.bg))))
      (line-number-minor-tick ((t (:foreground ,.dimmest :background ,.bg))))

      ;; --- mode line, header line, tabs --------------------------------------
      ;; A panel with a line edge; the active one carries the fuchsia rail,
      ;; laid across the top as the current tab's is.
      (mode-line ((t (:foreground ,.ink :background ,.panel :overline ,.pink
                      :box (:line-width (1 . 3) :color ,.panel)))))
      (mode-line-active ((t (:inherit mode-line))))
      (mode-line-inactive ((t (:foreground ,.muted :background ,.panel :overline ,.line
                               :box (:line-width (1 . 3) :color ,.panel)))))
      (mode-line-buffer-id ((t (:foreground ,.ink :weight normal))))
      (mode-line-emphasis ((t (:foreground ,.ink :weight normal))))
      (mode-line-highlight ((t (:foreground ,.pink :box nil))))
      (header-line ((t (:foreground ,.muted :background ,.panel
                        :box (:line-width (1 . 3) :color ,.panel)))))
      (header-line-highlight ((t (:foreground ,.pink))))
      (tab-bar ((t (:foreground ,.muted :background ,.panel))))
      (tab-bar-tab ((t (:foreground ,.ink :background ,.bg :overline ,.pink
                        :box (:line-width (6 . 3) :color ,.bg)))))
      (tab-bar-tab-inactive ((t (:foreground ,.muted :background ,.panel
                                 :box (:line-width (6 . 3) :color ,.panel)))))
      (tab-line ((t (:foreground ,.muted :background ,.panel))))
      (tab-line-tab ((t (:inherit tab-line))))
      (tab-line-tab-current ((t (:foreground ,.ink :background ,.bg :overline ,.pink))))
      (tab-line-tab-inactive ((t (:foreground ,.muted :background ,.panel))))
      (tab-line-highlight ((t (:foreground ,.pink))))

      ;; --- minibuffer, links, keys -------------------------------------------
      (minibuffer-prompt ((t (:foreground ,.purple))))
      (link ((t (:foreground ,.purple :underline (:color ,.ul-purple)))))
      (link-visited ((t (:inherit link))))
      (button ((t (:inherit link))))
      (help-key-binding ((t (:foreground ,.purple :background ,.wash-strong
                             :box (:line-width (1 . -1) :color ,.line)))))
      (help-argument-name ((t (:foreground ,.purple :slant italic))))
      (widget-field ((t (:foreground ,.ink :background ,.panel
                         :box (:line-width (1 . -1) :color ,.line)))))
      (widget-single-line-field ((t (:inherit widget-field))))
      (comint-highlight-prompt ((t (:foreground ,.purple))))
      (comint-highlight-input ((t (:foreground ,.ink))))
      (eshell-prompt ((t (:foreground ,.purple))))

      ;; --- font lock: four colors --------------------------------------------
      (font-lock-keyword-face ((t (:foreground ,.pink))))
      (font-lock-preprocessor-face ((t (:foreground ,.pink))))
      (font-lock-negation-char-face ((t (:foreground ,.pink))))
      (font-lock-string-face ((t (:foreground ,.string))))
      (font-lock-comment-face ((t (:foreground ,.muted :slant italic))))
      (font-lock-comment-delimiter-face ((t (:inherit font-lock-comment-face))))
      (font-lock-doc-face ((t (:foreground ,.muted :slant italic))))
      (font-lock-doc-markup-face ((t (:foreground ,.purple :slant italic))))
      (font-lock-constant-face ((t (:foreground ,.purple))))
      (font-lock-number-face ((t (:foreground ,.purple))))
      (font-lock-escape-face ((t (:foreground ,.purple))))
      (font-lock-type-face ((t (:foreground ,.purple))))
      (font-lock-builtin-face ((t (:foreground ,.purple))))
      (font-lock-regexp-grouping-backslash ((t (:foreground ,.purple))))
      (font-lock-regexp-grouping-construct ((t (:foreground ,.purple))))
      (font-lock-function-name-face ((t (:foreground ,.ink))))
      (font-lock-function-call-face ((t (:foreground ,.ink))))
      (font-lock-variable-name-face ((t (:foreground ,.ink))))
      (font-lock-variable-use-face ((t (:foreground ,.ink))))
      (font-lock-property-name-face ((t (:foreground ,.ink))))
      (font-lock-property-use-face ((t (:foreground ,.ink))))
      (font-lock-operator-face ((t (:foreground ,.ink))))
      (font-lock-punctuation-face ((t (:foreground ,.ink))))
      (font-lock-bracket-face ((t (:foreground ,.ink))))
      (font-lock-delimiter-face ((t (:foreground ,.ink))))
      (font-lock-misc-punctuation-face ((t (:foreground ,.ink))))
      (font-lock-warning-face ((t (:foreground ,.string))))

      ;; --- search: the current match is position, the rest are purple -------
      (isearch ((t (:foreground ,.bg :background ,.pink))))
      (isearch-group-1 ((t (:foreground ,.bg :background ,.purple))))
      (isearch-group-2 ((t (:foreground ,.bg :background ,.muted))))
      (isearch-fail ((t (:foreground ,.del :background ,.del-bg))))
      (lazy-highlight ((t (:foreground ,.ink :background ,.press))))
      (match ((t (:foreground ,.ink :background ,.press))))
      (query-replace ((t (:inherit isearch))))

      ;; --- parens ------------------------------------------------------------
      (show-paren-match ((t (:foreground ,.pink :background ,.wash-pink))))
      (show-paren-match-expression ((t (:background ,.wash))))
      (show-paren-mismatch ((t (:foreground ,.del :background ,.del-bg :underline t))))

      ;; --- completion --------------------------------------------------------
      ;; The current candidate is where you are: pink, on the current-line wash.
      (completions-common-part ((t (:foreground ,.purple))))
      (completions-first-difference ((t (:foreground ,.ink))))
      (completions-annotations ((t (:foreground ,.muted :slant italic))))
      (completions-highlight ((t (:foreground ,.pink :background ,.wash-strong))))
      (completions-group-title ((t (:foreground ,.muted))))
      (completions-group-separator ((t (:foreground ,.line :strike-through t))))
      (icomplete-selected-match ((t (:foreground ,.pink :background ,.wash-strong))))
      (vertico-current ((t (:foreground ,.pink :background ,.wash-strong :extend t))))
      (vertico-group-title ((t (:foreground ,.muted))))
      (vertico-group-separator ((t (:foreground ,.line :strike-through t))))
      (orderless-match-face-0 ((t (:foreground ,.purple))))
      (orderless-match-face-1 ((t (:foreground ,.string))))
      (orderless-match-face-2 ((t (:foreground ,.purple :underline t))))
      (orderless-match-face-3 ((t (:foreground ,.string :underline t))))
      (marginalia-documentation ((t (:foreground ,.muted :slant italic))))

      ;; --- diagnostics -------------------------------------------------------
      (flymake-error ((t (:underline (:style wave :color ,.del)))))
      (flymake-warning ((t (:underline (:style wave :color ,.string)))))
      (flymake-note ((t (:underline (:style wave :color ,.purple)))))
      (flycheck-error ((t (:underline (:style wave :color ,.del)))))
      (flycheck-warning ((t (:underline (:style wave :color ,.string)))))
      (flycheck-info ((t (:underline (:style wave :color ,.purple)))))
      (eglot-highlight-symbol-face ((t (:background ,.press))))
      (compilation-error ((t (:foreground ,.del))))
      (compilation-warning ((t (:foreground ,.string))))
      (compilation-info ((t (:foreground ,.add))))
      (compilation-line-number ((t (:foreground ,.purple))))
      (compilation-column-number ((t (:foreground ,.purple))))
      (compilation-mode-line-fail ((t (:foreground ,.del))))
      (compilation-mode-line-exit ((t (:foreground ,.add))))
      (compilation-mode-line-run ((t (:foreground ,.string))))

      ;; --- diff: text color, row tint, and the marker stays -----------------
      (diff-header ((t (:foreground ,.muted :background ,.panel :extend t))))
      (diff-file-header ((t (:foreground ,.muted :background ,.panel :weight normal :extend t))))
      (diff-hunk-header ((t (:foreground ,.purple :background ,.wash :extend t))))
      (diff-function ((t (:inherit diff-hunk-header))))
      (diff-index ((t (:inherit diff-file-header))))
      (diff-context ((t (:foreground ,.ink))))
      (diff-added ((t (:foreground ,.add :background ,.add-bg :extend t))))
      (diff-removed ((t (:foreground ,.del :background ,.del-bg :extend t))))
      (diff-changed ((t (:foreground ,.string :background ,.change-bg :extend t))))
      (diff-changed-unspecified ((t (:inherit diff-changed))))
      (diff-indicator-added ((t (:foreground ,.add :background ,.add-bg))))
      (diff-indicator-removed ((t (:foreground ,.del :background ,.del-bg))))
      (diff-indicator-changed ((t (:foreground ,.string :background ,.change-bg))))
      (diff-refine-added ((t (:foreground ,.ink :background ,.add-refine))))
      (diff-refine-removed ((t (:foreground ,.ink :background ,.del-refine))))
      (diff-refine-changed ((t (:foreground ,.ink :background ,.change-bg))))
      (diff-nonexistent ((t (:foreground ,.muted))))
      (diff-error ((t (:foreground ,.del))))
      (diff-hl-insert ((t (:foreground ,.add :background ,.add))))
      (diff-hl-delete ((t (:foreground ,.del :background ,.del))))
      (diff-hl-change ((t (:foreground ,.string :background ,.string))))

      ;; --- magit -------------------------------------------------------------
      ;; The hunk under point gets the current-line wash; its changed rows
      ;; step up to the bright ANSI color on a stronger tint.
      (magit-section-highlight ((t (:background ,.wash :extend t))))
      (magit-section-heading ((t (:foreground ,.muted :weight normal))))
      (magit-section-heading-selection ((t (:foreground ,.pink))))
      (magit-diff-file-heading ((t (:foreground ,.ink :weight normal))))
      (magit-diff-file-heading-highlight ((t (:background ,.wash :extend t))))
      (magit-diff-file-heading-selection ((t (:foreground ,.pink :background ,.wash))))
      (magit-diff-hunk-heading ((t (:foreground ,.purple :background ,.panel :extend t))))
      (magit-diff-hunk-heading-highlight ((t (:foreground ,.purple :background ,.press :extend t))))
      (magit-diff-hunk-heading-selection ((t (:foreground ,.pink :background ,.press :extend t))))
      (magit-diff-context ((t (:foreground ,.muted :extend t))))
      (magit-diff-context-highlight ((t (:foreground ,.ink :background ,.wash :extend t))))
      (magit-diff-added ((t (:foreground ,.add :background ,.add-bg :extend t))))
      (magit-diff-removed ((t (:foreground ,.del :background ,.del-bg :extend t))))
      (magit-diff-added-highlight ((t (:foreground ,.bright-green :background ,.add-bg-hl :extend t))))
      (magit-diff-removed-highlight ((t (:foreground ,.bright-red :background ,.del-bg-hl :extend t))))
      (magit-diff-base ((t (:foreground ,.string :background ,.change-bg :extend t))))
      (magit-diff-base-highlight ((t (:foreground ,.string :background ,.change-bg :extend t))))
      (magit-diff-whitespace-warning ((t (:background ,.del-bg))))
      (magit-diffstat-added ((t (:foreground ,.add))))
      (magit-diffstat-removed ((t (:foreground ,.del))))
      (magit-hash ((t (:foreground ,.muted))))
      (magit-branch-local ((t (:foreground ,.purple))))
      (magit-branch-remote ((t (:foreground ,.muted))))
      (magit-branch-current ((t (:foreground ,.pink))))
      (magit-head ((t (:foreground ,.pink))))
      (magit-tag ((t (:foreground ,.string))))
      (magit-dimmed ((t (:foreground ,.dimmest))))
      (magit-log-author ((t (:foreground ,.muted))))
      (magit-log-date ((t (:foreground ,.muted))))
      (magit-log-graph ((t (:foreground ,.muted))))
      (magit-process-ok ((t (:foreground ,.add))))
      (magit-process-ng ((t (:foreground ,.del))))

      ;; --- outline and org: mono, weight normal, no scaling ------------------
      ;; Levels 1 and 2 are ink, deeper levels muted, as the site's h3 and h4.
      (outline-1 ((t (:foreground ,.ink :weight normal :height 1.0))))
      (outline-2 ((t (:foreground ,.ink :weight normal :height 1.0))))
      (outline-3 ((t (:foreground ,.muted :weight normal :height 1.0))))
      (outline-4 ((t (:foreground ,.muted :weight normal :height 1.0))))
      (outline-5 ((t (:foreground ,.muted :weight normal :height 1.0))))
      (outline-6 ((t (:foreground ,.muted :weight normal :height 1.0))))
      (outline-7 ((t (:foreground ,.muted :weight normal :height 1.0))))
      (outline-8 ((t (:foreground ,.muted :weight normal :height 1.0))))
      (org-level-1 ((t (:inherit outline-1))))
      (org-level-2 ((t (:inherit outline-2))))
      (org-level-3 ((t (:inherit outline-3))))
      (org-level-4 ((t (:inherit outline-4))))
      (org-level-5 ((t (:inherit outline-5))))
      (org-level-6 ((t (:inherit outline-6))))
      (org-level-7 ((t (:inherit outline-7))))
      (org-level-8 ((t (:inherit outline-8))))
      (org-document-title ((t (:foreground ,.ink :weight normal :height 1.0))))
      (org-document-info ((t (:foreground ,.muted))))
      (org-document-info-keyword ((t (:foreground ,.muted))))
      (org-meta-line ((t (:foreground ,.muted))))
      (org-block ((t (:background ,.wash :extend t))))
      (org-block-begin-line ((t (:foreground ,.muted :background ,.wash :extend t))))
      (org-block-end-line ((t (:inherit org-block-begin-line))))
      (org-code ((t (:foreground ,.ink :background ,.wash-strong))))
      (org-verbatim ((t (:foreground ,.ink :background ,.wash-strong))))
      (org-quote ((t (:foreground ,.muted :slant italic))))
      (org-todo ((t (:foreground ,.string :weight normal))))
      (org-done ((t (:foreground ,.add :weight normal))))
      (org-headline-done ((t (:foreground ,.muted))))
      (org-date ((t (:foreground ,.purple :underline (:color ,.ul-purple)))))
      (org-link ((t (:inherit link))))
      (org-tag ((t (:foreground ,.muted :weight normal))))
      (org-table ((t (:foreground ,.ink))))
      (org-formula ((t (:foreground ,.purple))))
      (org-checkbox ((t (:foreground ,.muted))))
      (org-special-keyword ((t (:foreground ,.muted))))
      (org-drawer ((t (:foreground ,.muted))))
      (org-ellipsis ((t (:foreground ,.muted :underline nil))))
      (org-footnote ((t (:foreground ,.purple))))
      (org-priority ((t (:foreground ,.string))))

      ;; --- markdown ----------------------------------------------------------
      (markdown-header-face ((t (:foreground ,.ink :weight normal))))
      (markdown-code-face ((t (:background ,.wash :extend t))))
      (markdown-inline-code-face ((t (:foreground ,.ink :background ,.wash-strong))))
      (markdown-markup-face ((t (:foreground ,.muted))))
      (markdown-url-face ((t (:foreground ,.muted))))
      (markdown-blockquote-face ((t (:foreground ,.muted :slant italic))))

      ;; --- whitespace-mode ---------------------------------------------------
      (whitespace-space ((t (:foreground ,.dimmest))))
      (whitespace-tab ((t (:foreground ,.dimmest))))
      (whitespace-newline ((t (:foreground ,.dimmest))))
      (whitespace-trailing ((t (:background ,.del-bg))))
      (whitespace-line ((t (:foreground ,.string))))
      (whitespace-indentation ((t (:foreground ,.dimmest))))
      (whitespace-empty ((t (:background ,.wash))))

      ;; --- terminals: the Tilix palette --------------------------------------
      (ansi-color-black ((t (:foreground ,.ansi-black :background ,.ansi-black))))
      (ansi-color-red ((t (:foreground ,.ansi-red :background ,.ansi-red))))
      (ansi-color-green ((t (:foreground ,.ansi-green :background ,.ansi-green))))
      (ansi-color-yellow ((t (:foreground ,.ansi-yellow :background ,.ansi-yellow))))
      (ansi-color-blue ((t (:foreground ,.ansi-blue :background ,.ansi-blue))))
      (ansi-color-magenta ((t (:foreground ,.ansi-magenta :background ,.ansi-magenta))))
      (ansi-color-cyan ((t (:foreground ,.ansi-cyan :background ,.ansi-cyan))))
      (ansi-color-white ((t (:foreground ,.ansi-white :background ,.ansi-white))))
      (ansi-color-bright-black ((t (:foreground ,.ansi-bright-black :background ,.ansi-bright-black))))
      (ansi-color-bright-red ((t (:foreground ,.ansi-bright-red :background ,.ansi-bright-red))))
      (ansi-color-bright-green ((t (:foreground ,.ansi-bright-green :background ,.ansi-bright-green))))
      (ansi-color-bright-yellow ((t (:foreground ,.ansi-bright-yellow :background ,.ansi-bright-yellow))))
      (ansi-color-bright-blue ((t (:foreground ,.ansi-bright-blue :background ,.ansi-bright-blue))))
      (ansi-color-bright-magenta ((t (:foreground ,.ansi-bright-magenta :background ,.ansi-bright-magenta))))
      (ansi-color-bright-cyan ((t (:foreground ,.ansi-bright-cyan :background ,.ansi-bright-cyan))))
      (ansi-color-bright-white ((t (:foreground ,.ansi-bright-white :background ,.ansi-bright-white)))))))

(defun neon-doll-theme-apply (theme palette)
  "Set the Neon Doll faces for THEME from PALETTE."
  (apply #'custom-theme-set-faces theme (neon-doll-theme--faces palette)))

(provide 'neon-doll-theme-common)

;;; neon-doll-theme-common.el ends here
