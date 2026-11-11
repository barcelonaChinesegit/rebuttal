\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{Liebert_Author_R}[2020/22/09 v1.00
^^J LaTeX class file for Liebert Journals applicable for preparing manuscript at author's end]

\LoadClass[twoside]{article}

\usepackage{mathtools,amsthm,amsfonts,amssymb}%
\usepackage[round]{natbib}%
\usepackage[doublespacing]{setspace}%
\usepackage{threeparttable,booktabs}%
\usepackage{graphicx}%
\usepackage[figuresright]{rotating}%
\usepackage{enumitem}%

\newcommand{\keywords}[1]{\bgroup\noindent\textbf{Keywords:}
#1\egroup}%

\renewenvironment{abstract}{%
\begin{quote}\textbf{Abstract:} }%
{\end{quote}}%

\usepackage{hyperref}%

\usepackage[ruled]{algorithm2e}%

\usepackage{mathrsfs}%

\newtheorem{theorem}{Theorem}%
\newtheorem{lemma}{Lemma}%
\newtheorem{corollary}{Corollary}%
\newtheorem{remark}{Remark}%

\newtheorem*{theorem*}{Theorem}%
\newtheorem*{lemma*}{Lemma}%
\newtheorem*{corollary*}{Corollary}%
\newtheorem*{remark*}{Remark}%

\AtBeginDocument{\pagestyle{headings}}%

\newcommand{\notetocomp}[1]{\bgroup\parindent\z@\raggedright%
\marginpar{\footnotesize#1\par}
\egroup}%

\endinput