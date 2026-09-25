;;; scheme-emacs-sample.el --- Lay out a Neon Doll sample frame -*- lexical-binding: t -*-

;; Used by tools/scheme-shoot.sh under `emacs -Q'; loads the theme from
;; emacs/ in this repository without installing it.  Shows code with the
;; cursor on a paren and search hits, a diff, and an org buffer holding a
;; region, with the active and an inactive mode line and a tab bar.

;;; Code:

(require 'hl-line)
(require 'paren)
(require 'diff-mode)
(require 'org)

(defconst neon-doll-sample-code
  "/* four token colors, three already in the palette */
#include <stdio.h>

#define MODE \"drwxr-xr-x\"

struct row { const char *name; long size; };

static int render(const struct row *rows, size_t n, int width)
{
    for (size_t i = 0; i < n; i++) {
        /* TODO: clip to width */
        printf(\"%s %4ld %s\\n\", MODE, rows[i].size, rows[i].name);
    }
    return width > 80 ? -1 : 0;
}
")

(defconst neon-doll-sample-diff
  "diff --git a/src/Site/Block/Listing.php b/src/Site/Block/Listing.php
index 3f2a1c0..9b7d4e2 100644
--- a/src/Site/Block/Listing.php
+++ b/src/Site/Block/Listing.php
@@ -18,7 +18,7 @@ final class Listing implements Block
     public function render(): string
     {
-        return '<ul>' . $rows . '</ul>';
+        return '<ul class=\"ls\">' . $rows . '</ul>';
     }
 }
")

(defconst neon-doll-sample-org
  "#+title: neon-doll(7)
* Projects
** thinksynth
   A synthesizer that renders in the browser. [[https://example.org][home page]]
*** TODO Write the manual page
*** DONE Ship the jam mode
#+begin_src sh
  ls -l ~/log | head
#+end_src
Some ~inline code~ and =verbatim= text.
")

(defun neon-doll-sample--buffer (name text mode)
  "Return buffer NAME filled with TEXT in major MODE."
  (with-current-buffer (get-buffer-create name)
    (erase-buffer)
    (insert text)
    (funcall mode)
    (font-lock-ensure)
    (display-line-numbers-mode 1)
    (goto-char (point-min))
    (current-buffer)))

(defun neon-doll-sample--mark-search (buffer word current)
  "In BUFFER, paint every WORD as a lazy match and the CURRENT-th as isearch."
  (with-current-buffer buffer
    (save-excursion
      (goto-char (point-min))
      (let ((i 0))
        (while (search-forward word nil t)
          (overlay-put (make-overlay (match-beginning 0) (match-end 0))
                       'face (if (= i current) 'isearch 'lazy-highlight))
          (setq i (1+ i)))))))

(defun neon-doll-sample (variant root)
  "Show the Neon Doll VARIANT theme from ROOT/emacs on sample buffers."
  (add-to-list 'custom-theme-load-path (expand-file-name "emacs" root))
  (load-theme (intern (format "neon-doll-%s" variant)) t)
  (setq inhibit-startup-screen t
        highlight-nonselected-windows t
        show-paren-delay 0
        blink-cursor-mode nil)
  (blink-cursor-mode -1)
  (menu-bar-mode -1)
  (tool-bar-mode -1)
  (scroll-bar-mode -1)
  (tab-bar-mode 1)
  (tab-bar-new-tab)
  (tab-bar-rename-tab "notes")
  (tab-bar-select-tab 1)
  (tab-bar-rename-tab "code")
  (global-hl-line-mode 1)
  (show-paren-mode 1)
  (let ((code (neon-doll-sample--buffer "render.c" neon-doll-sample-code #'c-mode))
        (diff (neon-doll-sample--buffer "listing.diff" neon-doll-sample-diff #'diff-mode))
        (org (neon-doll-sample--buffer "notes.org" neon-doll-sample-org #'org-mode)))
    (neon-doll-sample--mark-search code "rows" 1)
    (with-current-buffer org
      (goto-char (point-min))
      (search-forward "A synthesizer")
      (set-mark (match-beginning 0))
      (goto-char (match-end 0))
      (activate-mark))
    (delete-other-windows)
    (switch-to-buffer code)
    (let ((bottom (split-window nil 19)))
      (set-window-buffer bottom diff)
      (set-window-buffer (split-window bottom 13) org))
    ;; The cursor just past the closing paren of printf (...).
    (with-current-buffer code
      (goto-char (point-min))
      (search-forward "rows[i].name)"))
    (set-window-point (selected-window) (with-current-buffer code (point)))
    (message "%s" (propertize "M-x load-theme RET neon-doll-" 'face 'minibuffer-prompt))))

;;; scheme-emacs-sample.el ends here
