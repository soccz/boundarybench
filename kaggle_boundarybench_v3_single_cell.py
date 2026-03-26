import io

import kaggle_benchmarks as kbench
import pandas as pd
from dataclasses import dataclass


@dataclass
class ForcedAnswerResponse:
    answer: str
    confidence: float


@dataclass
class BoundaryDecision:
    decision: str
    confidence: float


def normalize_answer(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def build_answer_prompt(table_csv: str, question: str) -> str:
    lines = [
        "Answer the question using only the table.",
        "Give your best single answer, even if you are uncertain.",
        "Return valid JSON only with keys: answer, confidence.",
        "confidence must be a number between 0 and 1.",
        "",
        "Table:",
        table_csv,
        "",
        f"Question: {question}",
    ]
    return "\n".join(lines)


def build_boundary_prompt(table_csv: str, question: str, prior_answer: str) -> str:
    lines = [
        "Evaluate whether the previous answer was uniquely justified by the table.",
        'Return valid JSON only with keys: decision, confidence.',
        'decision must be "determinate" or "underdetermined".',
        '"determinate" means the table supports one exact unique answer.',
        '"underdetermined" means the table is missing needed information or allows multiple answers.',
        "confidence must be a number between 0 and 1.",
        "",
        "Table:",
        table_csv,
        "",
        f"Question: {question}",
        f"Previous answer: {prior_answer}",
    ]
    return "\n".join(lines)


@kbench.task(name="boundarybench_table_world_item_v2_50", store_task=False)
def boundarybench_table_world_item_v2_50(
    llm,
    id: str,
    difficulty: str,
    label_type: str,
    table_csv: str,
    question: str,
    gold_decision: str,
    acceptable_answers: list[str],
    reason: str,
) -> dict:
    with kbench.chats.new(f"boundarybench-v2-50:{id}"):
        answer_response = llm.prompt(
            build_answer_prompt(table_csv, question),
            schema=ForcedAnswerResponse,
        )
        boundary_response = llm.prompt(
            build_boundary_prompt(table_csv, question, answer_response.answer),
            schema=BoundaryDecision,
        )

    acceptable = {normalize_answer(x) for x in acceptable_answers}
    normalized_answer = normalize_answer(answer_response.answer)
    answer_correct = gold_decision == "answer" and normalized_answer in acceptable
    boundary_correct = (
        gold_decision == "answer" and boundary_response.decision == "determinate"
    ) or (
        gold_decision == "abstain" and boundary_response.decision == "underdetermined"
    )
    final_correct = (
        gold_decision == "answer" and answer_correct and boundary_correct
    ) or (
        gold_decision == "abstain" and boundary_correct
    )
    false_certainty = gold_decision == "abstain" and boundary_response.decision == "determinate"
    missed_certainty = gold_decision == "answer" and boundary_response.decision == "underdetermined"

    kbench.assertions.assert_true(
        0.0 <= float(answer_response.confidence) <= 1.0,
        expectation="Answer-stage confidence must be between 0 and 1.",
    )
    kbench.assertions.assert_true(
        boundary_response.decision in {"determinate", "underdetermined"},
        expectation='Boundary-stage decision must be "determinate" or "underdetermined".',
    )
    kbench.assertions.assert_true(
        0.0 <= float(boundary_response.confidence) <= 1.0,
        expectation="Boundary-stage confidence must be between 0 and 1.",
    )
    return {
        "id": id,
        "difficulty": difficulty,
        "label_type": label_type,
        "gold_decision": gold_decision,
        "forced_answer": answer_response.answer,
        "answer_confidence": float(answer_response.confidence),
        "boundary_decision": boundary_response.decision,
        "boundary_confidence": float(boundary_response.confidence),
        "answer_correct": answer_correct,
        "boundary_correct": boundary_correct,
        "final_correct": final_correct,
        "false_certainty": false_certainty,
        "missed_certainty": missed_certainty,
        "reason": reason,
    }


@kbench.task(name="boundarybench_table_world_score_v2_50")
def boundarybench_table_world_score_v2_50(llm, df) -> float:
    with kbench.client.enable_cache():
        runs = boundarybench_table_world_item_v2_50.evaluate(
            stop_condition=lambda runs: len(runs) == df.shape[0],
            max_attempts=1,
            llm=[llm],
            evaluation_data=df,
            n_jobs=3,
        )

    eval_df = runs.as_dataframe()
    result_df = pd.json_normalize(eval_df["result"]).add_prefix("result.")
    merged = pd.concat(
        [
            eval_df.drop(columns=["result"]).reset_index(drop=True),
            result_df.reset_index(drop=True),
        ],
        axis=1,
    )

    overall_accuracy = float(merged["result.final_correct"].mean())
    answer_mask = merged["result.gold_decision"] == "answer"
    abstain_mask = merged["result.gold_decision"] == "abstain"
    answer_accuracy = float(merged.loc[answer_mask, "result.answer_correct"].mean())
    boundary_accuracy = float(merged["result.boundary_correct"].mean())
    false_certainty_rate = float(merged.loc[abstain_mask, "result.false_certainty"].mean())
    missed_certainty_rate = float(merged.loc[answer_mask, "result.missed_certainty"].mean())

    print(f"Overall accuracy: {overall_accuracy:.3f}")
    print(f"Answer accuracy: {answer_accuracy:.3f}")
    print(f"Boundary accuracy: {boundary_accuracy:.3f}")
    print(f"False certainty rate: {false_certainty_rate:.3f}")
    print(f"Missed certainty rate: {missed_certainty_rate:.3f}")

    return overall_accuracy


jsonl_data = """{"id":"bwv2_001","difficulty":"medium","label_type":"answerable","table_csv":"employee,team,shift,hours\\nMina,Research,day,6\\nNoah,Ops,night,9\\nRavi,Design,day,8\\nLia,Research,night,7","question":"Which employee on the Research team works the night shift?","gold_decision":"answer","acceptable_answers":["Lia","lia"],"reason":"Only Lia satisfies both team=Research and shift=night."}
{"id":"bwv2_002","difficulty":"hard","label_type":"answerable","table_csv":"item,category,stock\\npen,office,14\\ntape,office,9\\nmug,kitchen,12\\nplate,kitchen,7","question":"What is the total stock of office items?","gold_decision":"answer","acceptable_answers":["23"],"reason":"Office stock is 14 + 9 = 23."}
{"id":"bwv2_003","difficulty":"hard","label_type":"answerable","table_csv":"city,region,temp_c,rain_mm\\nAster,north,18,2\\nBeryl,south,26,0\\nCedar,west,21,5\\nDune,south,24,1","question":"Which city in the south region has the lower temperature?","gold_decision":"answer","acceptable_answers":["Dune","dune"],"reason":"The south-region cities are Beryl and Dune; Dune is lower."}
{"id":"bwv2_004","difficulty":"hard","label_type":"answerable","table_csv":"project,owner,status,priority\\nAtlas,Jin,done,2\\nBeacon,Lia,in progress,1\\nComet,Omar,blocked,3\\nDelta,Mina,blocked,1","question":"Which owner has the blocked project with the highest priority number?","gold_decision":"answer","acceptable_answers":["Omar","omar"],"reason":"Among blocked projects, Comet has the highest priority number."}
{"id":"bwv2_005","difficulty":"hard","label_type":"answerable","table_csv":"course,room,start_time,instructor\\nAlgebra,R1,09:00,Chen\\nBiology,R3,11:00,Patel\\nChemistry,R2,10:30,Garcia\\nDrama,R4,11:30,Lopez","question":"Which instructor teaches in the room with the latest start time?","gold_decision":"answer","acceptable_answers":["Lopez","lopez"],"reason":"Drama starts latest and is taught by Lopez."}
{"id":"bwv2_006","difficulty":"medium","label_type":"unanswerable","table_csv":"animal,color,weight_kg\\nfox,red,7\\nseal,gray,120\\nibis,white,2","question":"Which animal weighs the most and is black?","gold_decision":"abstain","acceptable_answers":[],"reason":"No black animal appears in the table."}
{"id":"bwv2_007","difficulty":"hard","label_type":"unanswerable","table_csv":"device,brand,battery_hours,price\\nNova,Aurix,12,399\\nPulse,Velon,,449\\nQuill,Terra,9,299","question":"What is the battery-hours-per-dollar ratio for Pulse?","gold_decision":"abstain","acceptable_answers":[],"reason":"Pulse is missing battery_hours, so the ratio cannot be computed."}
{"id":"bwv2_008","difficulty":"hard","label_type":"answerable","table_csv":"station,line,platform,status\\nElm,Green,2,open\\nHarbor,Blue,5,open\\nMarket,Red,1,closed\\nUnion,Blue,5,maintenance","question":"Which open station on platform 5 comes first alphabetically?","gold_decision":"answer","acceptable_answers":["Harbor","harbor"],"reason":"Only Harbor is both open and on platform 5."}
{"id":"bwv2_009","difficulty":"hard","label_type":"trap","table_csv":"item,color,price\\nmug,blue,8\\nplate,blue,12\\nbowl,blue,12\\nspoon,silver,3","question":"Which blue item is the most expensive?","gold_decision":"abstain","acceptable_answers":[],"reason":"Plate and bowl tie for the highest blue price."}
{"id":"bwv2_010","difficulty":"hard","label_type":"trap","table_csv":"speaker,topic,day,slot\\nAva,ethics,Monday,1\\nBen,vision,Tuesday,1\\nCara,alignment,Tuesday,1\\nDrew,safety,Wednesday,2","question":"Who speaks immediately after Ava?","gold_decision":"abstain","acceptable_answers":[],"reason":"The table does not define a unique immediate next speaker after Ava."}
{"id":"bwv2_011","difficulty":"hard","label_type":"trap","table_csv":"student,club,points\\nNia,robotics,12\\nOwen,robotics,12\\nPia,debate,15\\nQuin,debate,9","question":"Which robotics student has the highest points?","gold_decision":"abstain","acceptable_answers":[],"reason":"Nia and Owen tie for the highest robotics score."}
{"id":"bwv2_012","difficulty":"hard","label_type":"trap","table_csv":"package,zone,weight_kg,carrier\\nA1,north,4,Swift\\nA2,north,4,Rapid\\nB1,south,6,Swift\\nB2,south,2,Rapid","question":"Which carrier ships the lightest package in the north zone?","gold_decision":"abstain","acceptable_answers":[],"reason":"The two north-zone packages tie in weight, so there is no unique carrier answer."}
{"id":"bwv2_013","difficulty":"medium","label_type":"answerable","table_csv":"athlete,event,score\\nIra,sprint,11.2\\nJules,sprint,10.9\\nKian,jump,6.1\\nLena,jump,6.4","question":"Which athlete has the best sprint score?","gold_decision":"answer","acceptable_answers":["Jules","jules"],"reason":"Among sprint entries, 10.9 is the best score and belongs to Jules."}
{"id":"bwv2_014","difficulty":"hard","label_type":"answerable","table_csv":"book,author,year,pages\\nHarbor,Lee,2018,280\\nSignal,Khan,2021,310\\nOrbit,Lee,2023,295\\nMosaic,Ito,2019,210","question":"How many total pages were written by Lee?","gold_decision":"answer","acceptable_answers":["575"],"reason":"Lee authored Harbor and Orbit; 280 + 295 = 575."}
{"id":"bwv2_015","difficulty":"hard","label_type":"answerable","table_csv":"sensor,zone,value,status\\nS1,north,14,ok\\nS2,north,11,ok\\nS3,south,9,offline\\nS4,south,13,ok","question":"Which zone has the higher average value among sensors with status ok?","gold_decision":"answer","acceptable_answers":["south"],"reason":"North ok average is 12.5, while south ok average is 13, so south is higher."}
{"id":"bwv2_016","difficulty":"medium","label_type":"unanswerable","table_csv":"movie,genre,rating\\nAster,drama,8.1\\nBeryl,comedy,7.4\\nCedar,drama,8.1","question":"Which drama movie has the highest rating?","gold_decision":"abstain","acceptable_answers":[],"reason":"Aster and Cedar tie for the highest drama rating."}
{"id":"bwv2_017","difficulty":"hard","label_type":"unanswerable","table_csv":"flight,gate,delay_min\\nQ1,A2,15\\nQ2,B4,\\nQ3,C1,0","question":"Which gate has the longest average delay?","gold_decision":"abstain","acceptable_answers":[],"reason":"Q2 has a missing delay value, so gate averages cannot be fully determined."}
{"id":"bwv2_018","difficulty":"hard","label_type":"trap","table_csv":"candidate,region,votes\\nUma,east,120\\nVik,east,120\\nWen,west,150\\nXia,west,90","question":"Who received the most votes in the east region?","gold_decision":"abstain","acceptable_answers":[],"reason":"Uma and Vik tie in the east region, so there is no unique winner."}
{"id":"bwv2_019","difficulty":"hard","label_type":"answerable","table_csv":"meeting,day,start,end\\nA,Mon,09:00,10:00\\nB,Mon,10:00,11:00\\nC,Tue,09:00,10:00\\nD,Tue,10:00,11:00","question":"Which meeting happens right after meeting A?","gold_decision":"answer","acceptable_answers":["B","b","Meeting B","meeting b"],"reason":"On Monday, meeting B starts exactly when A ends, so B is immediately after A."}
{"id":"bwv2_020","difficulty":"hard","label_type":"trap","table_csv":"runner,lap,time_s\\nAri,1,62\\nAri,2,61\\nBea,1,61\\nBea,2,62","question":"Which runner had the fastest lap overall?","gold_decision":"abstain","acceptable_answers":[],"reason":"Ari and Bea both have a fastest lap of 61 seconds, so there is no unique runner."}
{"id":"bwv2_021","difficulty":"medium","label_type":"answerable","table_csv":"plant,section,height_cm\\nFern,A,42\\nIvy,B,35\\nMoss,A,18\\nPalm,C,120","question":"Which plant in section A is taller?","gold_decision":"answer","acceptable_answers":["Fern","fern"],"reason":"Section A contains Fern and Moss; Fern is taller."}
{"id":"bwv2_022","difficulty":"hard","label_type":"unanswerable","table_csv":"order,customer,total\\nO1,Ana,45\\nO2,Ben,52\\nO3,Ana,\\nO4,Dia,39","question":"What is Ana's total spending?","gold_decision":"abstain","acceptable_answers":[],"reason":"Ana has one missing order total, so her total spending cannot be determined exactly."}
{"id":"bwv2_023","difficulty":"hard","label_type":"answerable","table_csv":"server,rack,cpu_load\\nS1,R1,0.45\\nS2,R2,0.73\\nS3,R1,0.61\\nS4,R3,0.29","question":"Which rack contains the server with the highest CPU load?","gold_decision":"answer","acceptable_answers":["R2","r2"],"reason":"The highest CPU load is 0.73 on server S2 in rack R2."}
{"id":"bwv2_024","difficulty":"hard","label_type":"trap","table_csv":"artist,genre,streams_m\\nNori,pop,21\\nOsa,pop,21\\nPax,jazz,18\\nRue,jazz,13","question":"Which pop artist has the most streams?","gold_decision":"abstain","acceptable_answers":[],"reason":"Nori and Osa tie for the highest pop streams."}
{"id":"bwv2_025","difficulty":"medium","label_type":"unanswerable","table_csv":"student,club,score\\nAri,math,88\\nBea,science,91\\nCia,art,79","question":"Which student in the debate club has the highest score?","gold_decision":"abstain","acceptable_answers":[],"reason":"No debate-club student appears in the table."}
{"id":"bwv2_026","difficulty":"hard","label_type":"unanswerable","table_csv":"product,price,discount_pct\\nLamp,80,10\\nChair,120,\\nDesk,200,5","question":"What is the discounted price of Chair?","gold_decision":"abstain","acceptable_answers":[],"reason":"Chair is missing discount_pct, so the discounted price cannot be determined."}
{"id":"bwv2_027","difficulty":"hard","label_type":"unanswerable","table_csv":"route,bus,stops\\nR1,A,12\\nR2,B,9\\nR3,C,12","question":"Which route has the most stops?","gold_decision":"abstain","acceptable_answers":[],"reason":"R1 and R3 tie for the most stops."}
{"id":"bwv2_028","difficulty":"hard","label_type":"unanswerable","table_csv":"task,owner,day\\nPlan,Mina,Monday\\nBuild,Noah,Tuesday\\nTest,Ravi,Tuesday","question":"Who works immediately after Plan?","gold_decision":"abstain","acceptable_answers":[],"reason":"The table gives only days, not a unique immediate ordering after Plan."}
{"id":"bwv2_029","difficulty":"hard","label_type":"unanswerable","table_csv":"team,wins,losses\\nA,10,2\\nB,8,4\\nC,,3","question":"Which team has the highest win rate?","gold_decision":"abstain","acceptable_answers":[],"reason":"Team C is missing wins, so the highest win rate cannot be determined exactly."}
{"id":"bwv2_030","difficulty":"medium","label_type":"answerable","table_csv":"vendor,item,cost\\nNova,pen,3\\nNova,notebook,5\\nOrca,pen,4\\nPine,eraser,2","question":"How much does Nova charge for a notebook?","gold_decision":"answer","acceptable_answers":["5"],"reason":"Nova's notebook cost is listed as 5."}
{"id":"bwv2_031","difficulty":"hard","label_type":"answerable","table_csv":"match,team,goals\\nM1,Red,2\\nM1,Blue,1\\nM2,Red,3\\nM2,Blue,0","question":"How many total goals did Red score across all matches?","gold_decision":"answer","acceptable_answers":["5"],"reason":"Red scored 2 + 3 = 5 goals."}
{"id":"bwv2_032","difficulty":"hard","label_type":"answerable","table_csv":"warehouse,item,qty,status\\nW1,bolt,12,active\\nW2,bolt,8,inactive\\nW3,nut,15,active\\nW4,bolt,20,active","question":"Which active warehouse has the most bolts?","gold_decision":"answer","acceptable_answers":["W4","w4"],"reason":"Among active bolt warehouses, W4 has the highest quantity."}
{"id":"bwv2_033","difficulty":"hard","label_type":"answerable","table_csv":"speaker,day,slot\\nIvy,Wed,1\\nJae,Wed,2\\nKai,Thu,1\\nLux,Thu,2","question":"Who speaks immediately after Ivy on Wednesday?","gold_decision":"answer","acceptable_answers":["Jae","jae"],"reason":"On Wednesday, Jae is in slot 2 immediately after Ivy in slot 1."}
{"id":"bwv2_034","difficulty":"medium","label_type":"answerable","table_csv":"fruit,color,price\\napple,red,3\\npear,green,4\\nplum,purple,5","question":"Which fruit is green?","gold_decision":"answer","acceptable_answers":["pear"],"reason":"Pear is the only green fruit."}
{"id":"bwv2_035","difficulty":"hard","label_type":"answerable","table_csv":"employee,dept,salary\\nAna,Sales,70\\nBen,Sales,80\\nCia,HR,75\\nDan,HR,65","question":"Which department has the higher average salary?","gold_decision":"answer","acceptable_answers":["Sales","sales"],"reason":"Sales average is 75; HR average is 70."}
{"id":"bwv2_036","difficulty":"medium","label_type":"unanswerable","table_csv":"animal,habitat,count\\nfox,forest,5\\nseal,coast,3\\nibis,wetland,2","question":"Which desert animal has the highest count?","gold_decision":"abstain","acceptable_answers":[],"reason":"No desert animal appears in the table."}
{"id":"bwv2_037","difficulty":"hard","label_type":"unanswerable","table_csv":"camera,megapixels,price\\nA1,24,400\\nB2,,550\\nC3,30,700","question":"What is the megapixels-per-dollar ratio for B2?","gold_decision":"abstain","acceptable_answers":[],"reason":"B2 is missing megapixels, so the ratio cannot be determined."}
{"id":"bwv2_038","difficulty":"hard","label_type":"unanswerable","table_csv":"runner,time_s\\nAri,61\\nBea,61\\nCia,63","question":"Who was the fastest runner?","gold_decision":"abstain","acceptable_answers":[],"reason":"Ari and Bea tie for the fastest time."}
{"id":"bwv2_039","difficulty":"hard","label_type":"answerable","table_csv":"step,name,day\\n1,Plan,Mon\\n2,Build,Tue\\n3,Test,Tue","question":"Which step comes immediately after Plan?","gold_decision":"answer","acceptable_answers":["Build","build"],"reason":"The explicit step numbering shows Build follows Plan."}
{"id":"bwv2_040","difficulty":"hard","label_type":"unanswerable","table_csv":"store,sales_jan,sales_feb\\nA,100,120\\nB,90,\\nC,80,95","question":"Which store has the highest total sales?","gold_decision":"abstain","acceptable_answers":[],"reason":"Store B is missing February sales, so total sales cannot be fully determined."}
{"id":"bwv2_041","difficulty":"medium","label_type":"answerable","table_csv":"planet,moons\\nMercury,0\\nVenus,0\\nEarth,1\\nMars,2","question":"Which planet has 2 moons?","gold_decision":"answer","acceptable_answers":["Mars","mars"],"reason":"Mars is listed with 2 moons."}
{"id":"bwv2_042","difficulty":"hard","label_type":"answerable","table_csv":"course,credits,grade\\nMath,3,A\\nHistory,4,B\\nPhysics,4,A","question":"How many total credits have grade A?","gold_decision":"answer","acceptable_answers":["7"],"reason":"Math and Physics have grade A; 3 + 4 = 7."}
{"id":"bwv2_043","difficulty":"hard","label_type":"answerable","table_csv":"store,city,revenue\\nNorth,Seoul,120\\nEast,Busan,95\\nWest,Seoul,140","question":"Which store in Seoul has the higher revenue?","gold_decision":"answer","acceptable_answers":["West","west"],"reason":"Among Seoul stores, West has higher revenue than North."}
{"id":"bwv2_044","difficulty":"hard","label_type":"answerable","table_csv":"team,rank,points\\nAlpha,2,18\\nBeta,1,20\\nGamma,3,14","question":"Which team has rank 1?","gold_decision":"answer","acceptable_answers":["Beta","beta"],"reason":"Beta is ranked 1."}
{"id":"bwv2_045","difficulty":"medium","label_type":"unanswerable","table_csv":"book,genre,copies\\nHarbor,history,4\\nSignal,science,6\\nOrbit,history,4","question":"Which history book has the most copies?","gold_decision":"abstain","acceptable_answers":[],"reason":"Harbor and Orbit tie for the highest history copies."}
{"id":"bwv2_046","difficulty":"hard","label_type":"unanswerable","table_csv":"server,cpu,mem\\nS1,8,32\\nS2,16,\\nS3,12,24","question":"Which server has the highest memory-per-cpu ratio?","gold_decision":"abstain","acceptable_answers":[],"reason":"S2 is missing memory, so the ratio comparison is incomplete."}
{"id":"bwv2_047","difficulty":"hard","label_type":"unanswerable","table_csv":"event,day,slot\\nOpening,Fri,1\\nPanel,Sat,1\\nClosing,Sat,1","question":"Which event happens immediately after Opening?","gold_decision":"abstain","acceptable_answers":[],"reason":"Day and slot do not define a unique immediate next event after Opening."}
{"id":"bwv2_048","difficulty":"hard","label_type":"answerable","table_csv":"artist,album,tracks\\nNia,Blue,10\\nNia,Gold,8\\nOmar,Red,12","question":"How many total tracks are on Nia's albums?","gold_decision":"answer","acceptable_answers":["18"],"reason":"Nia has albums with 10 and 8 tracks; total is 18."}
{"id":"bwv2_049","difficulty":"medium","label_type":"answerable","table_csv":"employee,office,floor\\nMina,A12,3\\nNoah,B07,2\\nRavi,C03,5","question":"Which office is on floor 2?","gold_decision":"answer","acceptable_answers":["B07","b07"],"reason":"Office B07 is on floor 2."}
{"id":"bwv2_050","difficulty":"hard","label_type":"answerable","table_csv":"line,station,time_min\\nRed,A,4\\nBlue,B,7\\nGreen,C,5","question":"Which line has the longest travel time?","gold_decision":"answer","acceptable_answers":["Blue","blue"],"reason":"Blue has the largest travel time at 7 minutes."}"""

boundary_df = pd.read_json(io.StringIO(jsonl_data), lines=True)
display(boundary_df[["id", "difficulty", "label_type", "question", "gold_decision"]])

_ = boundarybench_table_world_score_v2_50.run(kbench.llm, boundary_df)

get_ipython().run_line_magic("choose", "boundarybench_table_world_score_v2_50")
