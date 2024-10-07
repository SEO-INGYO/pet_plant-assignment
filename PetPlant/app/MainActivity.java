package com.example.petplant;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.Socket;
import java.util.ArrayList;
import java.util.Random;

public class MainActivity extends AppCompatActivity
{
    EditText IPAddres_EditText; // IP주소 입력할 텍스트입력창
    EditText Port_EditText; // 포트번호 입력할 텍스트입력창
    android.widget.Button ConnectionServer_button; // 서버 연결 버튼
    Spinner PlantList_spinner; // 식물리스트 스피너
    TextView SunValue_textview; // 직사광선 값 텍스트뷰
    TextView TempValue_textview; // 온도 값 텍스트뷰
    TextView WaterValue_textview; // 토양 내 습도 값 텍스트뷰
    android.widget.Button PlantBook_button;
    android.widget.Button PlantCondition_button;
    android.widget.Button GiveWater_button;
    android.widget.Button GiveSun_button;
    android.widget.Button PlantBanner_button;

    private String str;
    private ArrayList<String> arrayList;
    private ArrayAdapter<String> arrayAdapter;
    private String address;
    private int port;
    private String sendPlant;
    private Socket socket;
    private ArrayList<String> tipList;
    private Handler handler = new Handler();
    private Random random = new Random();

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        tipList = new ArrayList<>();
        tipList.add("Tip. 음료를 마시고 남은 플라스틱은 온실 화분으로 사용하기 아주 좋은 재료에요.");
        tipList.add("Tip. 화분에 쓸 흙을 야외에서 아무거나 가져오면 집안에 개미, 바퀴벌레들이 들어올 수 있어요.");
        tipList.add("Tip. 광량이 부족한 환경이 되면 식물이 길고 연약하게 자라는 웃자람 현상이 발생할 수 있어요.");
        tipList.add("Tip. 물을 과하게 주면 식물에 곰팡이가 필 수도 있어요.");
        tipList.add("Tip. 대부분의 화분들은 평균적으로 물을 '겉흙이 말랐을 때 흠뻑' 주면 좋아요.");
        tipList.add("Tip. 식충식물에게 벌레를 잡아서 먹일 필요는 없어요.");

        IPAddres_EditText = findViewById(R.id.IPAddress); // IP 입력 텍스트 입력 창
        Port_EditText = findViewById(R.id.Port); // IP 입력 텍스트 입력 창

        PlantList_spinner = findViewById(R.id.PlantList);

        SunValue_textview = findViewById(R.id.SunValue); // 햇빛의 양 텍스트 창
        TempValue_textview = findViewById(R.id.TempValue); // 현재 온도 텍스트 창
        WaterValue_textview = findViewById(R.id.WaterValue); // 화분 습도 텍스트 창

        PlantBanner_button = findViewById(R.id.PlantBanner); // 식물팁 배너

        PlantBanner_button.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View view)
            {
                int i;
                i = random.nextInt(5);
                PlantBanner_button.setText(tipList.get(i));
            }
        });

        PlantList_spinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener()
        {
            @Override
            public void onItemSelected(AdapterView<?> adapterView, View view, int i, long l)
            {
                sendPlant  = arrayList.get(i);
            }

            @Override
            public void onNothingSelected(AdapterView<?> adapterView)
            {

            }
        });

        ConnectionServer_button = findViewById(R.id.ConnectionServer);

        ConnectionServer_button.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View view)
            {
                address = IPAddres_EditText.getText().toString().trim();
                port = Integer.parseInt(Port_EditText.getText().toString());
                str = "서버연결";

                ClientThread clientthread = new ClientThread(address,port);
                SendThread sendthread = new SendThread(socket,str);
                ReceivePlantThread receiveplantthread = new ReceivePlantThread(socket);

                try
                {
                    clientthread.start();
                    clientthread.join();

                    sendthread.start();
                    sendthread.join();

                    receiveplantthread.start();
                    receiveplantthread.join();
                }
                catch (InterruptedException e)
                {
                    e.printStackTrace();
                }
            }
        });

        PlantBook_button = findViewById(R.id.PlantBook); // 식물도감 열기 버튼

        PlantBook_button.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View view)
            {
                Intent intent = new Intent(Intent.ACTION_VIEW); // 액티비티끼리 호출하기 위한
                Uri uri = Uri.parse("https://terms.naver.com/list.naver?cid=42526&categoryId=42526"); // 통합 자원 식별자
                intent.setData(uri); // intent 를 통해 uri 링크를 담는다.
                startActivity(intent); // 액티비티 실행
            }
        });

        PlantCondition_button = findViewById(R.id.PlantCondition); // 식물상태  갱신 버튼

        PlantCondition_button.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View view)
            {
                address = IPAddres_EditText.getText().toString().trim();
                port = Integer.parseInt(Port_EditText.getText().toString());
                str = "식물상태확인";
                str = str + sendPlant;

                ClientThread clientthread = new ClientThread(address,port);
                SendThread sendthread = new SendThread(socket,str);
                ReceiveConditonThread receiveconditonthread = new ReceiveConditonThread(socket);

                try
                {
                    clientthread.start();
                    clientthread.join();

                    sendthread.start();
                    sendthread.join();

                    receiveconditonthread.start();
                    receiveconditonthread.join();
                }
                catch (InterruptedException e)
                {
                    e.printStackTrace();
                }
            }
        });

        GiveWater_button = findViewById(R.id.GiveWater); // 식물상태  갱신 버튼

        GiveWater_button.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View view)
            {
                address = IPAddres_EditText.getText().toString().trim();
                port = Integer.parseInt(Port_EditText.getText().toString());
                str = "물주기";
                str = str + sendPlant;

                ClientThread clientthread = new ClientThread(address,port);
                SendThread sendthread = new SendThread(socket,str);

                try
                {
                    clientthread.start();
                    clientthread.join();

                    sendthread.start();
                    sendthread.join();
                }
                catch (InterruptedException e)
                {
                    e.printStackTrace();
                }
            }
        });

        GiveSun_button = findViewById(R.id.GiveSun); // 식물상태  갱신 버튼

        GiveSun_button.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View view)
            {
                address = IPAddres_EditText.getText().toString().trim();
                port = Integer.parseInt(Port_EditText.getText().toString());
                str = "빛조정";
                str = str + sendPlant;

                ClientThread clientthread = new ClientThread(address,port);
                SendThread sendthread = new SendThread(socket,str);

                try
                {
                    clientthread.start();
                    clientthread.join();

                    sendthread.start();
                    sendthread.join();
                }
                catch (InterruptedException e)
                {
                    e.printStackTrace();
                }
            }
        });
    }

    class ClientThread extends Thread
    {
        String host; // 서버 IP
        int port;

        public ClientThread(String host, int port)
        {
            this.host = host;
            this.port = port;
        }

        public void run()
        {
            try
            {
                socket = new Socket(host, port);
            }
            catch(Exception e)
            {
                e.printStackTrace();
            }
        }
    }

    class SendThread extends Thread
    {
        Socket socket;
        String data;

        public SendThread(Socket socket, String data)
        {
            this.socket = socket;
            this.data = data;
        }

        public void run()
        {
            try
            {
                BufferedWriter bufferedWriter = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
                bufferedWriter.write(data);
                bufferedWriter.newLine();
                bufferedWriter.flush();
            }
            catch (Exception e)
            {
                e.printStackTrace();
            }

        }
    }

    class ReceivePlantThread extends  Thread
    {
        Socket socket;

        public ReceivePlantThread(Socket socket)
        {
            this.socket = socket;
        }

        public void run()
        {
            try
            {
                BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                String clientMessage = bufferedReader.readLine();

                if(clientMessage == "오류")
                {
                    handler.post(new Runnable()
                    {
                        @Override
                        public void run()
                        {
                            Toast.makeText(MainActivity.this, "서버 연결을 확인해주세요.", Toast.LENGTH_LONG).show();
                        }
                    });
                }
                else
                {
                    String[] data = clientMessage.split(",");

                    handler.post(new Runnable()
                    {
                        @Override
                        public void run()
                        {
                            arrayList = new ArrayList<>();
                            arrayList.add(data[0]);
                            arrayList.add(data[1]);
                            arrayAdapter = new ArrayAdapter<>(getApplicationContext(), android.R.layout.simple_spinner_dropdown_item, arrayList);
                            PlantList_spinner.setAdapter(arrayAdapter);
                        }
                    });
                }
            }
            catch(Exception e)
            {
                e.printStackTrace();
            }
        }
    }

    class ReceiveConditonThread extends  Thread
    {
        Socket socket;

        public ReceiveConditonThread(Socket socket)
        {
            this.socket = socket;
        }

        public void run()
        {
            try
            {
                BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                String clientMessage = bufferedReader.readLine();

                if(clientMessage == "오류")
                {
                    handler.post(new Runnable()
                    {
                        @Override
                        public void run()
                        {
                            Toast.makeText(MainActivity.this, "서버 연결을 확인해주세요.", Toast.LENGTH_LONG).show();
                        }
                    });
                }
                else
                {
                    String[] data = clientMessage.split(",");

                    handler.post(new Runnable()
                    {
                        @Override
                        public void run()
                        {
                            SunValue_textview.setText(data[0]);
                            WaterValue_textview.setText(data[1]);
                            TempValue_textview.setText(data[2]);
                        }
                    });
                }
            }
            catch(Exception e)
            {
                e.printStackTrace();
            }
        }
    }
}