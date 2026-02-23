// @ts-check
// @type {import('@docusaurus/types').Config}
import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Truth Network',
  tagline: '真相網 - 資訊素養與事實查證研究',
  favicon: 'img/favicon.ico',

  // 設定 GitHub Pages URL
  url: 'https://your-username.github.io',
  baseUrl: '/truth-network-site/',

  // 組織與專案設定
  organizationName: 'your-username',
  projectName: 'truth-network-site',

  // GitHub Pages 部署設定
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  onDuplicateRoutes: 'warn',

  // 預設語言與國際化
  i18n: {
    defaultLocale: 'zh-TW',
    locales: ['zh-TW', 'en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // 編輯 URL
          editUrl: 'https://github.com/your-username/truth-network-site/tree/main/',
        },
        blog: false, // 不使用部落格功能
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // 導航欄設定
      navbar: {
        title: 'Truth Network',
        logo: {
          alt: 'Truth Network Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: '研究文章',
          },
          {
            type: 'docsVersionDropdown',
            position: 'right',
          },
          {
            type: 'localeDropdown',
            position: 'right',
          },
          {
            href: 'https://github.com/your-username/trtruth-network-site',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      // 頁腳設定
      footer: {
        style: 'dark',
        copyright: `Copyright © ${new Date().getFullYear()} Truth Network. Built with Docusaurus.`,
      },
      // Prism 語法高亮設定
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
      // 色彩主題
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
    }),
};

export default config;
