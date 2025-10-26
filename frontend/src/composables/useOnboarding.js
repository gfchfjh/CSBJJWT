/**
 * ✅ P1-5优化：新手引导 Composable
 * 使用 driver.js 实现分步高亮引导
 */

import { driver } from "driver.js"
import "driver.js/dist/driver.css"

export function useOnboarding() {
  /**
   * 启动新手引导
   */
  const startOnboarding = () => {
    const driverObj = driver({
      showProgress: true,
      showButtons: ['next', 'previous', 'close'],
      steps: [
        {
          element: '.nav-item-home',
          popover: {
            title: '📊 欢迎来到主页！',
            description: '这里显示今日转发统计、成功率和实时状态。您可以一眼看到系统运行情况。',
            side: "right",
            align: 'start'
          }
        },
        {
          element: '.service-control-card',
          popover: {
            title: '🎮 服务控制中心',
            description: '在这里启动、停止或重启转发服务。启动后，系统会自动监听KOOK消息并转发。',
            side: "bottom"
          }
        },
        {
          element: '.nav-item-accounts',
          popover: {
            title: '👤 KOOK账号管理',
            description: '首先需要添加KOOK账号。您可以使用账号密码登录，或导入Cookie（推荐）。',
            side: "right"
          }
        },
        {
          element: '.nav-item-bots',
          popover: {
            title: '🤖 机器人配置',
            description: '添加Discord、Telegram或飞书机器人，作为消息转发的目标平台。',
            side: "right"
          }
        },
        {
          element: '.nav-item-mapping',
          popover: {
            title: '🔀 频道映射配置',
            description: '设置KOOK频道到目标平台的映射关系。支持可视化拖拽和智能匹配！',
            side: "right"
          }
        },
        {
          element: '.nav-item-filter',
          popover: {
            title: '🔧 过滤规则',
            description: '设置关键词过滤、用户黑白名单等规则，精确控制哪些消息需要转发。',
            side: "right"
          }
        },
        {
          element: '.nav-item-logs',
          popover: {
            title: '📋 实时日志',
            description: '查看所有转发记录、成功率和失败原因。支持搜索和筛选。',
            side: "right"
          }
        },
        {
          element: '.nav-item-settings',
          popover: {
            title: '⚙️ 系统设置',
            description: '调整图片处理策略、日志级别、通知方式等高级设置。',
            side: "right"
          }
        },
        {
          popover: {
            title: '🎉 引导完成！',
            description: '您已了解主要功能模块。现在可以开始配置：\n\n1. 添加KOOK账号\n2. 配置转发机器人\n3. 设置频道映射\n4. 启动转发服务\n\n祝您使用愉快！'
          }
        }
      ],
      nextBtnText: '下一步 →',
      prevBtnText: '← 上一步',
      doneBtnText: '完成',
      progressText: '{{current}} / {{total}}',
      onDestroyStarted: () => {
        // 引导结束时，标记已完成
        localStorage.setItem('onboarding_completed', 'true')
        driverObj.destroy()
      }
    })

    driverObj.drive()
  }

  /**
   * 快速配置引导（仅核心步骤）
   */
  const startQuickOnboarding = () => {
    const driverObj = driver({
      showProgress: true,
      steps: [
        {
          popover: {
            title: '⚡ 快速开始',
            description: '接下来3步，完成基础配置：'
          }
        },
        {
          element: '.nav-item-accounts',
          popover: {
            title: '步骤1：添加KOOK账号',
            description: '点击这里，添加您的第一个KOOK账号',
            side: "right"
          }
        },
        {
          element: '.nav-item-bots',
          popover: {
            title: '步骤2：配置转发机器人',
            description: '选择Discord、Telegram或飞书，配置机器人',
            side: "right"
          }
        },
        {
          element: '.nav-item-mapping',
          popover: {
            title: '步骤3：设置频道映射',
            description: '建立KOOK频道到目标平台的映射关系',
            side: "right"
          }
        },
        {
          popover: {
            title: '✅ 配置完成！',
            description: '配置完成后，返回主页启动服务即可开始转发消息'
          }
        }
      ],
      nextBtnText: '下一步',
      prevBtnText: '上一步',
      doneBtnText: '开始配置',
      onDestroyed: () => {
        // 引导结束后，跳转到账号管理页
        window.location.href = '#/accounts'
      }
    })

    driverObj.drive()
  }

  /**
   * 功能演示引导
   */
  const startFeatureDemo = (feature) => {
    const demos = {
      'smart-mapping': {
        steps: [
          {
            element: '.smart-mapping-button',
            popover: {
              title: '🧙 智能映射',
              description: '一键自动匹配同名或相似的KOOK频道和目标频道',
              side: "bottom"
            }
          },
          {
            element: '.mapping-confidence',
            popover: {
              title: '📊 置信度评分',
              description: '系统会给出每个映射的置信度评分，帮助您判断匹配准确度',
              side: "top"
            }
          }
        ]
      },
      'visual-mapping': {
        steps: [
          {
            element: '.source-panel',
            popover: {
              title: '📥 拖拽源频道',
              description: '从左侧KOOK频道列表中拖拽频道',
              side: "right"
            }
          },
          {
            element: '.target-panel',
            popover: {
              title: '📤 放置到目标',
              description: '将频道拖放到右侧的Bot卡片中，即可建立映射',
              side: "left"
            }
          }
        ]
      }
    }

    const demoSteps = demos[feature]
    if (!demoSteps) return

    const driverObj = driver({
      showProgress: true,
      steps: demoSteps.steps
    })

    driverObj.drive()
  }

  /**
   * 检查是否需要显示引导
   */
  const shouldShowOnboarding = () => {
    return !localStorage.getItem('onboarding_completed')
  }

  return {
    startOnboarding,
    startQuickOnboarding,
    startFeatureDemo,
    shouldShowOnboarding
  }
}
