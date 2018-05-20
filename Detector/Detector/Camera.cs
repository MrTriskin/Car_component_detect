using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Drawing.Imaging;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Threading;
using System.IO;
using GxIAPINET;
using GxIAPINET.Sample.Common;
using System.Reflection;

namespace GxSingleCam
{
    public partial class Camera
    {
        #region 变量声明
        IGXFactory m_objIGXFactory = null;                            ///<Factory对像
        IGXDevice m_objIGXDevice = null;                            ///<设备对像
        IGXStream m_objIGXStream = null;                            ///<流对像
        IGXFeatureControl m_objIGXFeatureControl = null;             ///<远端设备属性控制器对像
        GxBitmap m_objGxBitmap = null;                            ///<图像显示类对象
        string strSingleShotName = "";
        string m_strFilePath = "";                              ///<应用程序当前路径
        string str_MySN = "";

        #endregion

        public Camera()
        {
            // 获取应用程序的当前执行路径
            m_strFilePath = Directory.GetCurrentDirectory().ToString();
        }

        #region 相机底层函数
        /// <summary>
        /// 相机初始化
        /// </summary>
        void __InitDevice()
        {
            if (null != m_objIGXFeatureControl)
            {
                //设置采集模式连续采集
                m_objIGXFeatureControl.GetEnumFeature("AcquisitionMode").SetValue("Continuous");
            }
        }

        /// <summary>
        /// 关闭流
        /// </summary>
        private void __CloseStream()
        {
            try
            {
                //关闭流
                if (null != m_objIGXStream)
                {
                    m_objIGXStream.Close();
                    m_objIGXStream = null;
                }
            }
            catch (Exception)
            {
            }
        }

        /// <summary>
        /// 关闭设备
        /// </summary>
        private void __CloseDevice()
        {
            try
            {
                //关闭设备
                if (null != m_objIGXDevice)
                {
                    m_objIGXDevice.Close();
                    m_objIGXDevice = null;
                }
            }
            catch (Exception)
            {
            }
        }
        #endregion

        #region 拍摄功能
        /// 拍摄单张
        public void SingleShot(string save_path)
        {
            strSingleShotName = save_path;
            try
            {
                m_objIGXFactory = IGXFactory.GetInstance();
                m_objIGXFactory.Init();

                List<IGXDeviceInfo> listGXDeviceInfo = new List<IGXDeviceInfo>();

                //关闭流
                __CloseStream();
                // 如果设备已经打开则关闭，保证相机在初始化出错情况下能再次打开
                __CloseDevice();

                m_objIGXFactory.UpdateDeviceList(200, listGXDeviceInfo);

                // 判断当前连接设备个数
                if (listGXDeviceInfo.Count <= 0)
                {
                    MessageBox.Show("未发现设备!");
                    return;
                }

                str_MySN = listGXDeviceInfo[0].GetSN();
                m_objIGXDevice = m_objIGXFactory.OpenDeviceBySN(str_MySN, GX_ACCESS_MODE.GX_ACCESS_EXCLUSIVE);
                if (null == m_objIGXDevice)
                {
                    MessageBox.Show(string.Format("未能打开相机{0}设备。", str_MySN));
                    return;
                }

                m_objGxBitmap = new GxBitmap(m_objIGXDevice);
                m_objIGXFeatureControl = m_objIGXDevice.GetRemoteFeatureControl();
                if (null == m_objIGXFeatureControl)
                {
                    MessageBox.Show(string.Format("未获得相机{0}属性控制。", str_MySN));
                    return;
                }
                m_objIGXStream = m_objIGXDevice.OpenStream(0);
                if (null == m_objIGXStream)
                {
                    MessageBox.Show(string.Format("相机{0}获取流失败。", str_MySN));
                }

                //初始化相机参数
                m_objIGXFeatureControl.GetEnumFeature("AcquisitionMode").SetValue("Continuous");
                m_objIGXFeatureControl.GetEnumFeature("TriggerMode").SetValue("Off");

                //打开流，获得单帧图像
                m_objIGXStream.StartGrab();
                m_objIGXFeatureControl.GetCommandFeature("AcquisitionStart").Execute();
                IImageData singleImageData = m_objIGXStream.GetImage(100);
                m_objIGXFeatureControl.GetCommandFeature("AcquisitionStop").Execute();
                m_objIGXFeatureControl = null;
                m_objIGXStream.StopGrab();
                __CloseStream();
                __CloseDevice();
                m_objIGXFactory.Uninit();
                if (!Directory.Exists(m_strFilePath)) Directory.CreateDirectory(m_strFilePath);
                strSingleShotName = m_strFilePath + "\\" + strSingleShotName;
                m_objGxBitmap.SaveBmp(singleImageData, strSingleShotName);
                return;

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }
        #endregion

        //回调函数
        private void __CaptureCallbackOneShot(object objUserParam, IFrameData objIFrameData)
        {
            try
            {
                Camera objCamera = objUserParam as Camera;
                string stfFileName = m_strFilePath + "\\" + strSingleShotName;  // 默认的图像保存名称
                m_objGxBitmap.SaveBmp(objIFrameData, stfFileName);
            }
            catch (Exception)
            {
            }
        }
        

    }
}
