from __future__ import annotations

from backend.core.schemas import DramaProjectRequest, ScriptDoctorReport, ScriptRevisionItem, ScriptStructureBeat, StoryDevelopment


def build_script_doctor_report(project: DramaProjectRequest, story: StoryDevelopment) -> ScriptDoctorReport:
    lead_role = project.roles[0] if project.roles else "女主"
    second_role = project.roles[1] if len(project.roles) > 1 else "男主"
    total = max(project.episodes, 10)
    midpoint = max(6, min(total // 2, 30))

    structure = [
        ScriptStructureBeat(
            stage="开场压迫",
            episodes="1",
            purpose="3 秒内让观众知道主角被谁压迫、为什么必须反击。",
            must_have=["公开羞辱或重大损失", "反派明确出手", "主角不是无辜解释而是被迫行动"],
        ),
        ScriptStructureBeat(
            stage="交易入局",
            episodes="2",
            purpose=f"让{second_role}进入主线，把情感关系和利益关系绑定在一起。",
            must_have=["合作条件", "代价或把柄", "反派第一次试探两人关系"],
        ),
        ScriptStructureBeat(
            stage="第一次爽点",
            episodes="3",
            purpose="给观众第一次回报，同时设置付费卡点。",
            must_have=["主角小胜", "证据公开或身份线索", "更大的秘密出现"],
        ),
        ScriptStructureBeat(
            stage="关系升温与误会",
            episodes=f"4-{midpoint}",
            purpose="用误会、保护和利益冲突推动追更。",
            must_have=["关系拉扯", "反派升级压迫", "阶段性筹码交换"],
        ),
        ScriptStructureBeat(
            stage="中段大反转",
            episodes=str(midpoint),
            purpose="揭开一个关键身份或旧案真相，制造二次爆点。",
            must_have=["身份反转", "旧证据翻盘", "关系立场变化"],
        ),
        ScriptStructureBeat(
            stage="终局清算",
            episodes=f"{max(total - 8, midpoint + 1)}-{total}",
            purpose="集中回收伏笔，让主角完成情感和利益双线胜利。",
            must_have=["反派失控", "主角主动设局", "关系承诺或事业翻盘"],
        ),
    ]

    content_optimizations = [
        "把第1集开场从背景介绍改成冲突现场，先给羞辱、背叛或损失，再补原因。",
        "每集只保留一个主冲突，删除不推动反击、误会或付费卡点的支线。",
        f"强化{lead_role}的主动选择，避免连续被动受害，让观众相信她能逆袭。",
        f"{lead_role}和{second_role}每 2-3 集必须有一次关系推进或立场反转。",
        "第3、6、10集的结尾不要用普通悬念，要用身份、证据、关系失控这类强付费点。",
        "投流版本的台词要更短，单句尽量 12 字以内，方便字幕和信息流理解。",
    ]

    revision_items = [
        ScriptRevisionItem(
            target="第1集开场",
            problem="如果先讲背景，短视频用户容易在前 3 秒流失。",
            suggestion="改成主角被当众否定、解除合作或被亲近者背叛的现场。",
            example=f"{lead_role}刚上台就被抢走成果，反派当众宣布她出局。",
        ),
        ScriptRevisionItem(
            target="第2集关系",
            problem=f"{second_role}只提供资源会显得工具化，缺少情感拉力。",
            suggestion="给合作加一个代价，比如交换证据、假装关系或共同承担风险。",
            example=f"{second_role}答应帮忙，但要求{lead_role}公开站到他这一边。",
        ),
        ScriptRevisionItem(
            target="第3集付费点",
            problem="第一次反击如果只解决小矛盾，付费欲望不够强。",
            suggestion="让小胜牵出更大秘密，把观众停在真相门口。",
            example="证据公开后，反派脱口说出当年还有另一个操盘者。",
        ),
        ScriptRevisionItem(
            target="中段节奏",
            problem="连续推进容易疲劳，需要周期性反转。",
            suggestion="每 4 集安排一次关系反转或筹码失效，避免只有反派压迫。",
            example="主角刚拿到证据，却发现证人已经被男主阵营藏起来。",
        ),
    ]

    dialogue_rewrites = [
        "原：你们为什么要这样对我？ -> 改：今天这笔账，我会一笔一笔要回来。",
        "原：我真的没有做错。 -> 改：我不解释了，证据会替我说话。",
        "原：谢谢你帮我。 -> 改：你不是在帮我，你是在赌我能赢。",
        "原：我不会放过你的。 -> 改：别急，下一个公开道歉的人就是你。",
    ]

    shootable_structure = [
        "主场景控制在公司大厅、办公室、家中、走廊 4 类，降低转场成本。",
        "前三集每集 3 个场景：冲突现场、私下交易、结尾反转。",
        "核心演员控制在 3-4 人，群演只用于第1集公开羞辱和第3集反击现场。",
        "每集预留 1 条可剪成投流素材的强台词，拍摄时单独补一个近景版本。",
    ]

    return ScriptDoctorReport(
        structure=structure,
        content_optimizations=content_optimizations,
        revision_items=revision_items,
        dialogue_rewrites=dialogue_rewrites,
        shootable_structure=shootable_structure,
    )
